
# Documentação do Backend – Vitrine Online

Este backend foi desenvolvido com **Python (Flask)** e tem como objetivo servir como API para uma vitrine digital de produtos. A estrutura do backend é simples e foca em funcionalidades essenciais como cadastro de produtos, geração de descrições com IA, e conexão com banco de dados.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.11+**
- **Flask** — Microframework para criação da API.
- **psycopg** — Conector com banco de dados PostgreSQL.
- **python-dotenv** — Para uso de variáveis de ambiente.
- **Google Gemini API** — Geração automática de descrições de produtos.

---

## 📁 Estrutura de Pastas

```
backend/
│
├── app.py                # Ponto de entrada principal do Flask
├── gerar_descricao.py   # Integração com a API Gemini
├── db.py                # Conexão com o banco PostgreSQL
├── .env                 # Variáveis de ambiente (não comitar)
└── requirements.txt     # Dependências do projeto
```

---

## 🔑 Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do backend com as seguintes variáveis:

```
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_banco
GEMINI_API_KEY=sua_chave_da_api_google
```

---

## 🚀 Como Executar o Backend

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sua-vitrine.git
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie o arquivo `.env` com as chaves necessárias.

4. Execute o servidor:
```bash
python app.py
```

---

## 🔌 Endpoints Disponíveis

### `GET /produtos`
Retorna todos os produtos cadastrados.

### `POST /produtos`
Cadastra um novo produto.
**Body JSON esperado:**
```json
{
  "nome": "Camiseta Masculina",
  "categoria": "Vestuário"
}
```

### `POST /descricao`
Gera uma descrição automática via IA Gemini.
**Body JSON esperado:**
```json
{
  "nome_produto": "Camiseta Masculina",
  "categoria": "Vestuário"
}
```

---

## 🧠 Geração de Descrição com Gemini

Arquivo: `gerar_descricao.py`

A função `gerar_descricao_gemini(nome_produto, categoria)` envia um prompt para a API da Gemini e retorna uma descrição coerente, fluida e pronta para uso. Também há uma função opcional `ajustar_texto()` para substituir placeholders.

---

## 🔗 Conexão com Banco de Dados

Arquivo: `db.py`

A função `get_connection()` conecta ao banco PostgreSQL usando a URL armazenada na variável de ambiente `DATABASE_URL`.

---

## ✅ Requisitos

- Python 3.11+
- Conta Google com acesso à API Gemini (https://aistudio.google.com)
- PostgreSQL ativo com tabela de produtos, se necessário.

---

## 📌 Observações

- Evite versionar o arquivo `.env`.
- A chave da Gemini API possui cota gratuita, mas pode requerer ativação do faturamento.
- Este backend pode ser conectado facilmente ao frontend Angular já existente via chamadas HTTP.

---

## ✍️ Autora

Desireê Costa  
Desenvolvedora Web Júnior  
[LinkedIn](https://linkedin.com/in/desiree-cost4) 
