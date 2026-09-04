"""
veridis — upload para o AWS S3

Pega os arquivos JSON gerados pelo extract.py (em data/raw/) e sobe
para o bucket S3, organizados em pastas por tipo de dado e data
"""

import os
import glob
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def get_s3_client():
    """Cria e retorna um cliente autenticado do S3."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def upload_file(s3_client, local_path, s3_key):
    """Sobe um único arquivo para o S3."""
    s3_client.upload_file(local_path, AWS_BUCKET_NAME, s3_key)
    print(f"  Enviado: {s3_key}")


def run_upload():
    s3 = get_s3_client()

    # Pega todos os arquivos .json dentro de data/raw/
    local_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.json"))

    if not local_files:
        print("Nenhum arquivo JSON encontrado em data/raw/. Rode o extract.py primeiro.")
        return

    print(f"Encontrados {len(local_files)} arquivos para enviar...\n")

    for local_path in local_files:
        filename = os.path.basename(local_path)

        # Organiza no S3 por tipo de dado (ex: top_tracks/top_tracks_2026-09-03.json)
        # Isso simula uma estrutura de "particionamento", comum em data lakes reais
        data_type = filename.split("_2")[0]  # pega o nome antes da data
        s3_key = f"raw/{data_type}/{filename}"

        upload_file(s3, local_path, s3_key)

    print("\nUpload concluído! Confira o bucket no console da AWS.")


if __name__ == "__main__":
    run_upload()
