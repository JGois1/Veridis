"""
veridis — carregar dados no banco SQLite

Pega os CSVs já limpos (em data/processed/) e carrega num banco de
dados SQLite (data/veridis.db). SQLite não precisa de servidor — o
banco inteiro é um único arquivo, ideal pra projetos de portfólio.

Cada CSV vira uma tabela com o mesmo nome (sem o .csv).
"""

import os
import glob
import sqlite3
import pandas as pd

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "veridis.db")


def load_csv_to_table(conn, csv_path):
    """Lê um CSV e carrega como tabela no banco, usando o nome do
    arquivo (sem .csv) como nome da tabela."""
    table_name = os.path.splitext(os.path.basename(csv_path))[0]
    df = pd.read_csv(csv_path)

    # if_exists="replace": toda vez que rodar o script, a tabela é
    # recriada do zero com os dados mais recentes do CSV
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"  Tabela '{table_name}' criada com {len(df)} linhas")


def run_load():
    conn = sqlite3.connect(DB_PATH)

    csv_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "*.csv"))

    if not csv_files:
        print("Nenhum CSV encontrado em data/processed/. Rode o transform.py primeiro.")
        return

    print(f"Carregando {len(csv_files)} arquivos para o banco...\n")

    for csv_path in csv_files:
        load_csv_to_table(conn, csv_path)

    conn.close()
    print(f"\nBanco criado em: {DB_PATH}")


if __name__ == "__main__":
    run_load()
