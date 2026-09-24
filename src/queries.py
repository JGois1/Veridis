"""
veridis — consultas SQL de exemplo

Roda algumas queries interessantes sobre os dados carregados no
banco SQLite, respondendo perguntas reais sobre seus hábitos de escuta.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "veridis.db")


def run_query(conn, titulo, query):
    #Roda uma query e imprime o resultado formatado.
    print(f"\n{'=' * 60}")
    print(titulo)
    print("=" * 60)
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def main():
    conn = sqlite3.connect(DB_PATH)

    # 1. Quais artistas mais aparecem no seu top de faixas?
    run_query(conn, "TOP 10 ARTISTAS (por número de faixas no seu top)", """
        SELECT artista, COUNT(*) AS numero_de_faixas
        FROM top_tracks
        GROUP BY artista
        ORDER BY numero_de_faixas DESC
        LIMIT 10;
    """)

    # 2. Suas faixas mais longas
    run_query(conn, "5 FAIXAS MAIS LONGAS DO SEU TOP", """
        SELECT nome_faixa, artista, duracao_min
        FROM top_tracks
        ORDER BY duracao_min DESC
        LIMIT 5;
    """)

    # 3. Distribuição por década de lançamento
    run_query(conn, "SUAS FAIXAS TOP POR DÉCADA DE LANÇAMENTO", """
        SELECT
            (CAST(SUBSTR(data_lancamento, 1, 4) AS INTEGER) / 10) * 10 AS decada,
            COUNT(*) AS numero_de_faixas
        FROM top_tracks
        WHERE data_lancamento != 'indisponível'
        GROUP BY decada
        ORDER BY decada;
    """)

    # 4. Artistas que aparecem tanto no top quanto nas curtidas (cruzando tabelas)
    run_query(conn, "ARTISTAS QUE APARECEM NO TOP *E* NAS CURTIDAS", """
        SELECT DISTINCT t.artista
        FROM top_tracks t
        INNER JOIN saved_tracks s ON t.artista = s.artista
        ORDER BY t.artista;
    """)

    # 5. Quantas faixas distintas você tocou recentemente
    run_query(conn, "TOTAL DE FAIXAS DISTINTAS TOCADAS RECENTEMENTE", """
        SELECT COUNT(DISTINCT nome_faixa) AS faixas_distintas
        FROM recently_played;
    """)

    # 6. Em que dia da semana você mais escuta música?
    run_query(conn, "ESCUTAS POR DIA DA SEMANA", """
        SELECT
            CASE CAST(strftime('%w', tocada_em) AS INTEGER)
                WHEN 0 THEN 'Domingo'
                WHEN 1 THEN 'Segunda'
                WHEN 2 THEN 'Terça'
                WHEN 3 THEN 'Quarta'
                WHEN 4 THEN 'Quinta'
                WHEN 5 THEN 'Sexta'
                WHEN 6 THEN 'Sábado'
            END AS dia_da_semana,
            COUNT(*) AS numero_de_escutas
        FROM recently_played
        GROUP BY dia_da_semana
        ORDER BY numero_de_escutas DESC;
    """)

    # 7. Em que horário do dia você mais escuta música?
    run_query(conn, "ESCUTAS POR FAIXA DE HORÁRIO", """
        SELECT
            CASE
                WHEN CAST(strftime('%H', tocada_em) AS INTEGER) BETWEEN 6 AND 11 THEN 'Manhã (6h-12h)'
                WHEN CAST(strftime('%H', tocada_em) AS INTEGER) BETWEEN 12 AND 17 THEN 'Tarde (12h-18h)'
                WHEN CAST(strftime('%H', tocada_em) AS INTEGER) BETWEEN 18 AND 23 THEN 'Noite (18h-24h)'
                ELSE 'Madrugada (0h-6h)'
            END AS faixa_horario,
            COUNT(*) AS numero_de_escutas
        FROM recently_played
        GROUP BY faixa_horario
        ORDER BY numero_de_escutas DESC;
    """)

    conn.close()


if __name__ == "__main__":
    main()
