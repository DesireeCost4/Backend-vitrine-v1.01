# Importa o módulo 'os' para acessar variáveis de ambiente do sistema
import os

# Importa o módulo 'psycopg' para conectar ao banco de dados PostgreSQL
import psycopg

# Importa a função 'load_dotenv' para carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv

# Carrega as variáveis de ambiente definidas no arquivo .env
load_dotenv()

# Função responsável por obter a conexão com o banco de dados PostgreSQL
def get_connection():
    # Recupera a URL de conexão do banco de dados da variável de ambiente DATABASE_URL
    url = os.getenv("DATABASE_URL")
    
    # Se a variável não estiver definida, levanta uma exceção
    if not url:
        raise Exception("A variável DATABASE_URL não foi encontrada.")
    
    # Retorna a conexão com o banco de dados usando a URL fornecida
    return psycopg.connect(url)
print("Conexão realizada com sucesso!")
