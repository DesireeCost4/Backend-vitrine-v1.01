import os
import psycopg
import base64
from dotenv import load_dotenv

load_dotenv()

def write_cert():
    cert_base64 = os.getenv("ROOT_CERT_BASE64")
    if not cert_base64:
        raise Exception("A variável ROOT_CERT_BASE64 não foi encontrada.")
    cert_path = "/tmp/root.crt"
    with open(cert_path, "wb") as f:
        f.write(base64.b64decode(cert_base64))
    return cert_path

def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("A variável DATABASE_URL não foi encontrada.")
    cert_path = write_cert()
    return psycopg.connect(url, sslrootcert=cert_path, sslmode="verify-full")

print("Conexão realizada com sucesso!")
