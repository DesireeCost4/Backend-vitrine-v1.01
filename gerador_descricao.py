import requests

# Chave de API do Google Gemini. Substitua por sua própria chave válida.
API_KEY = 'AIzaSyAwmVhCL1ejUF8pmA1uqNXjl_iOq1zunfs'

def gerar_descricao_gemini(nome_produto, categoria, API_KEY):
    """
    Gera uma descrição de produto usando a API do Gemini 2.0 Flash (Google).

    Parâmetros:
    - nome_produto (str): Nome do produto.
    - categoria (str): Categoria em que o produto se enquadra.
    - API_KEY (str): Chave de autenticação para acesso à API do Gemini.

    Retorna:
    - str: Descrição gerada pela IA, ou None em caso de erro.
    """
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}'

    # Prompt personalizado com instruções claras para a IA gerar a descrição.
    prompt = (
        f"Você é um assistente útil. Gere uma descrição criativa, completa e objetiva para o produto abaixo. "
        f"Use um texto corrido, fluido e bem formatado, pronto para usar, sem opções múltiplas.\n"
        f"Nome: {nome_produto}\n"
        f"Categoria: {categoria}\n"
        f"Descrição:"
    )

    headers = {
        'Content-Type': 'application/json'
    }

    # Corpo da requisição contendo o prompt.
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    # Envia requisição para a API.
    response = requests.post(url, headers=headers, json=data)
    resposta_json = response.json()

    # Valida se a resposta contém candidatos válidos e retorna o texto.
    if 'candidates' in resposta_json:
        texto_gerado = resposta_json['candidates'][0]['content']['parts'][0]['text']
        return texto_gerado.strip()
    else:
        # Log de erro para depuração.
        print("Erro: 'candidates' não encontrado na resposta.")
        print(resposta_json)
        return None

def ajustar_texto(texto):
    """
    Ajusta o texto gerado pela IA substituindo placeholders por dados reais.

    Parâmetros:
    - texto (str): Texto gerado pela IA.

    Retorna:
    - str: Texto ajustado com substituições prontas para uso.
    """
    if texto is None:
        return None

    # Substitui placeholders genéricos por valores reais.
    texto = texto.replace("[inserir tipo de tecido]", "algodão premium")
    texto = texto.replace("[Inserir cores e tamanhos disponíveis]", "preto, branco e cinza; tamanhos P, M, G e GG")
    return texto

if __name__ == "__main__":
    # Executa o programa como script: coleta dados, gera descrição e imprime.
    nome = input("Nome do produto: ")
    categoria = input("Categoria do produto: ")
    descricao = gerar_descricao_gemini(nome, categoria, API_KEY)
    descricao_ajustada = ajustar_texto(descricao)

    print("\nDescrição gerada pela IA ajustada:")
    print(descricao_ajustada if descricao_ajustada else "Nenhuma descrição gerada.")
