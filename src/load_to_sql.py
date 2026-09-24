"""
veridis — carregar dados no banco PostgreSQL (AWS RDS)

Pega os CSVs já limpos (em data/processed/) e carrega num banco de
dados PostgreSQL hospedado no AWS RDS. Usamos SQLAlchemy como "ponte"
entre pandas e o banco — é a forma padrão de conectar pandas a bancos
relacionais que não sejam SQLite.

Cada CSV vira uma tabela com o mesmo nome (sem o .csv).
"""

import os
import glob
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_engine():
    """Cria e retorna uma engine de conexão do SQLAlchemy com o Postgres."""
    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return create_engine(connection_string)


# Colunas que representam datas/horários. Precisamos convertê-las
# explicitamente, senão o pandas as lê como texto puro, e o Postgres
# cria a coluna como TEXT em vez de TIMESTAMP (quebrando funções de
# data como EXTRACT()).
COLUNAS_DE_DATA = ["tocada_em", "curtida_em"]


def load_csv_to_table(engine, csv_path):
    """Lê um CSV e carrega como tabela no banco, usando o nome do
    arquivo (sem .csv) como nome da tabela."""
    table_name = os.path.splitext(os.path.basename(csv_path))[0]
    df = pd.read_csv(csv_path)

    for coluna in COLUNAS_DE_DATA:
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

    # if_exists="replace": toda vez que rodar o script, a tabela é
    # recriada do zero com os dados mais recentes do CSV
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"  Tabela '{table_name}' criada com {len(df)} linhas")


def run_load():
    engine = get_engine()

    csv_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "*.csv"))

    if not csv_files:
        print("Nenhum CSV encontrado em data/processed/. Rode o transform.py primeiro.")
        return

    print(f"Carregando {len(csv_files)} arquivos para o banco...\n")

    for csv_path in csv_files:
        load_csv_to_table(engine, csv_path)

    print(f"\nDados carregados no banco '{DB_NAME}' em {DB_HOST}")


if __name__ == "__main__":
    run_load()
