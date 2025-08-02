# Importações principais
from flask import Flask, jsonify, request  # Flask para criar a API, jsonify para respostas JSON, request para acessar dados da requisição
from flask_cors import CORS  # Lib para liberar o CORS (acesso de domínios diferentes, como o frontend)
import os
import psycopg  # Conexão com o banco de dados PostgreSQL
from dotenv import load_dotenv  # Para carregar variáveis de ambiente do .env
import base64  # Para codificar imagem binária para base64

# Importa funções auxiliares da IA
from gerador_descricao import gerar_descricao_gemini, ajustar_texto

# Inicializa o app Flask e permite CORS
app = Flask(__name__)
CORS(app)

# Carrega variáveis do .env
API_KEY = os.getenv("API_KEY")
  # Minha chave da API do Gemini (Google AI)
load_dotenv()
url = os.getenv("DATABASE_URL")  # Lê a URL do banco

if not url:
    raise Exception("A variável DATABASE_URL não está definida no .env")


# Se estiver em produção, recria o arquivo root.crt a partir da variável de ambiente
if os.getenv("RENDER") == "true":  # variável automática da Render
    cert_path = os.path.expanduser("~/.postgresql")
    os.makedirs(cert_path, exist_ok=True)
    with open(os.path.join(cert_path, "root.crt"), "wb") as f:
        f.write(base64.b64decode(os.environ["ROOT_CERT_BASE64"]))
    ssl_cert_path = os.path.join(cert_path, "root.crt")
else:
    ssl_cert_path = "certs/root.crt"  # Caminho local para desenvolvimento

# Conecta ao banco para verificar se está tudo ok
conn = psycopg.connect(
    url,
    sslrootcert="certs/root.crt",
    sslmode="verify-full") # Só imprime a data/hora atual como teste de conexão

# ROTA DE IA: gera descrição automática com Gemini AI
@app.route("/descricao", methods=["POST"])
def descricao():
    data = request.json
    nome = data.get("nome")
    categoria = data.get("categoria")

    # Verifica se os campos foram enviados
    if not nome or not categoria:
        return jsonify({"error": "Informe nome e categoria do produto"}), 400

    # Gera e ajusta o texto com IA
    texto = gerar_descricao_gemini(nome, categoria, API_KEY)
    texto_ajustado = ajustar_texto(texto)

    # Retorna o resultado ou erro
    if texto_ajustado:
        return jsonify({"descricao": texto_ajustado})
    else:
        return jsonify({"error": "Não foi possível gerar a descrição"}), 500

# Função utilitária para conectar ao banco
def get_db_connection():
    return psycopg.connect(os.environ['DATABASE_URL'])


# Rota simples para teste
@app.route('/')
def home():
    return '<h1>API de Produtos Online</h1><p>Acesse /produtos para ver os produtos.</p>'

# ROTA DE CADASTRO (CREATE)
@app.route('/admin/produtos', methods=['POST'])
def cadastrar_produto():
    
    
    print("request.form:", request.form)          
    print("request.files:", request.files)        
    print("imagem:", request.files.get('imagem'))  

    
    
    # Lê dados do formulário enviado via multipart/form-data
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    categoria = request.form.get('categoria')
    estoque = request.form.get('estoque')
    descricao = request.form.get('descricao')
    imagem = request.files.get('imagem')

    # Verifica se todos os campos foram preenchidos
    campos_obrigatorios = {
        "nome": nome,
        "preco": preco,
        "categoria": categoria,
        "estoque": estoque,
        ##"imagem": imagem,
        "descricao": descricao
    }

    for campo, valor in campos_obrigatorios.items():
        if not valor:
            return jsonify({"erro": f"O campo '{campo}' é obrigatório."}), 400

    imagem_bytes = imagem.read()  # Converte imagem para bytes para salvar no banco

    # Insere no banco
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO produtos (nome, preco, categoria, estoque, descricao, imagem)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (nome, float(preco), categoria, int(estoque), descricao, imagem_bytes))
        novo_id = cur.fetchone()[0]
        conn.commit()

    return jsonify({
        "mensagem": "Produto cadastrado com sucesso!",
        "produto": {
            "id": novo_id,
            "nome": nome,
            "preco": float(preco),
            "categoria": categoria,
            "descricao": descricao,
            "imagem": "imagem salva no banco como binário",
            "estoque": int(estoque)
        }
    }), 201



# ROTA DE ATUALIZAÇÃO (UPDATE)
@app.route('/produtos/<int:id>', methods=['PATCH'])
def editar_produto(id):
    # Campos opcionais para edição
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    descricao = request.form.get('descricao')
    imagem = request.files.get('imagem')

    # Garante que pelo menos 1 campo foi enviado
    if not any([nome, preco, descricao, imagem]):
        return jsonify({"erro": "Informe pelo menos um campo para atualizar."}), 400

    conn = get_db_connection()
    with conn.cursor() as cur:
        # Verifica se o produto existe
        cur.execute("SELECT id FROM produtos WHERE id = %s", (id,))
        produto = cur.fetchone()
        if not produto:
            return jsonify({"erro": "Produto não encontrado."}), 404

        # Monta SQL dinamicamente
        campos = []
        valores = []

        if nome:
            campos.append("nome = %s")
            valores.append(nome)
        if preco:
            try:
                valores.append(float(preco))
                campos.append("preco = %s")
            except:
                return jsonify({"erro": "Preço inválido."}), 400
        if descricao:
            campos.append("descricao = %s")
            valores.append(descricao)
        if imagem:
            imagem_bytes = imagem.read() if imagem else None
            campos.append("imagem = %s")
            valores.append(imagem_bytes)

        valores.append(id)
        sql = f"UPDATE produtos SET {', '.join(campos)} WHERE id = %s"
        cur.execute(sql, valores)
        conn.commit()

    return jsonify({"mensagem": "Produto atualizado com sucesso."}), 200


# ROTA DE DELETE
@app.route('/produtos/<int:id>', methods=['DELETE'])
def apagar_produto(id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Verifica se o produto existe
        cur.execute("SELECT id FROM produtos WHERE id = %s", (id,))
        produto = cur.fetchone()
        if not produto:
            return jsonify({"erro": "Produto não encontrado."}), 404

        # Apaga do banco
        cur.execute("DELETE FROM produtos WHERE id = %s", (id,))
        conn.commit()

    return jsonify({"mensagem": "Produto apagado com sucesso."}), 200

# ROTA PARA LISTAR TODOS (READ)
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    busca = request.args.get('busca', default='', type=str).strip()

    conn = get_db_connection()
    with conn.cursor() as cur:
        if busca:
            cur.execute("""
                SELECT id, nome, preco, categoria, estoque, descricao, imagem
                FROM produtos
                WHERE nome ILIKE %s
            """, ('%' + busca + '%',))
        else:
            cur.execute("""
                SELECT id, nome, preco, categoria, estoque, descricao, imagem
                FROM produtos
            """)
        rows = cur.fetchall()

    produtos = []
    for row in rows:
        imagem_bytes = None
        imagem_b64 = None
        try:
            imagem_bytes = row[6]
            if imagem_bytes:
                imagem_b64 = base64.b64encode(imagem_bytes).decode('utf-8')
        except Exception as e:
            print(f"Erro ao converter imagem para base64: {e}")

        produtos.append({
            "id": str(row[0]),
            "nome": row[1],
            "preco": float(row[2]),
            "categoria": row[3],
            "estoque": int(row[4]),
            "descricao": row[5],
            "imagem": imagem_b64
        })

    return jsonify(produtos)

# ROTA PARA DETALHE DE UM PRODUTO
@app.route('/produtos/<id>', methods=['GET'])
def obter_produto(id):
    print(f"ID recebido na rota: {id} (tipo: {type(id)})")

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, nome, preco, categoria, estoque, descricao, imagem
            FROM produtos WHERE id = %s
        """, (id,))
        row = cur.fetchone()

    if row:
        # aqui você tem a imagem em row[6]
        imagem_bytes = row[6]
        print(f"imagem_bytes type: {type(imagem_bytes)}")  # Debug movido para cá

        produto = {
            "id": row[0],
            "nome": row[1],
            "preco": float(row[2]),
            "categoria": row[3],
            "estoque": int(row[4]),
            "descricao": row[5],
            "imagem": base64.b64encode(imagem_bytes).decode('utf-8') if imagem_bytes else None
        }
        return jsonify(produto)
    else:
        return jsonify({"erro": "Produto não encontrado"}), 404

# ROTA DE LOGIN SIMULADA (sem autenticação real por enquanto)
admin_user = {
    "email": "admin@email.com",
    "senha": "123456"
}

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')

    if email == admin_user['email'] and senha == admin_user['senha']:
        return jsonify({"success": True, "token": "admin321"}), 200
    else:
        return jsonify({"success": False, "message": "Credenciais Inválidas"}), 401

# Inicia o servidor com debug ativado
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
