"""
veridis — consultas SQL de exemplo

Roda algumas queries interessantes sobre os dados carregados no
banco PostgreSQL, respondendo perguntas reais sobre seus hábitos de escuta.

Nota: as funções de data mudaram em relação à versão SQLite. O Postgres
usa EXTRACT(DOW FROM ...) e EXTRACT(HOUR FROM ...) em vez de strftime().
"""

from load_to_sql import get_engine
import pandas as pd


def run_query(engine, titulo, query):
    """Roda uma query e imprime o resultado formatado."""
    print(f"\n{'=' * 60}")
    print(titulo)
    print("=" * 60)
    df = pd.read_sql_query(query, engine)
    print(df.to_string(index=False))
    return df


def main():
    engine = get_engine()

    # 1. Quais artistas mais aparecem no seu top de faixas?
    run_query(engine, "TOP 10 ARTISTAS (por número de faixas no seu top)", """
        SELECT artista, COUNT(*) AS numero_de_faixas
        FROM top_tracks
        GROUP BY artista
        ORDER BY numero_de_faixas DESC
        LIMIT 10;
    """)

    # 2. Suas faixas mais longas
    run_query(engine, "5 FAIXAS MAIS LONGAS DO SEU TOP", """
        SELECT nome_faixa, artista, duracao_formatada
        FROM top_tracks
        ORDER BY duracao_min DESC
        LIMIT 5;
    """)

    # 3. Distribuição por década de lançamento
    run_query(engine, "SUAS FAIXAS TOP POR DÉCADA DE LANÇAMENTO", """
        SELECT
            (CAST(SUBSTRING(data_lancamento FROM 1 FOR 4) AS INTEGER) / 10) * 10 AS decada,
            COUNT(*) AS numero_de_faixas
        FROM top_tracks
        WHERE data_lancamento != 'indisponível'
        GROUP BY decada
        ORDER BY decada;
    """)

    # 4. Artistas que aparecem tanto no top quanto nas curtidas (cruzando tabelas)
    run_query(engine, "ARTISTAS QUE APARECEM NO TOP *E* NAS CURTIDAS", """
        SELECT DISTINCT t.artista
        FROM top_tracks t
        INNER JOIN saved_tracks s ON t.artista = s.artista
        ORDER BY t.artista;
    """)

    # 5. Quantas faixas distintas você tocou recentemente
    run_query(engine, "TOTAL DE FAIXAS DISTINTAS TOCADAS RECENTEMENTE", """
        SELECT COUNT(DISTINCT nome_faixa) AS faixas_distintas
        FROM recently_played;
    """)

    # 6. Em que dia da semana você mais escuta música?
    run_query(engine, "ESCUTAS POR DIA DA SEMANA", """
        SELECT
            CASE EXTRACT(DOW FROM tocada_em)
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
    run_query(engine, "ESCUTAS POR FAIXA DE HORÁRIO", """
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM tocada_em) BETWEEN 6 AND 11 THEN 'Manhã (6h-12h)'
                WHEN EXTRACT(HOUR FROM tocada_em) BETWEEN 12 AND 17 THEN 'Tarde (12h-18h)'
                WHEN EXTRACT(HOUR FROM tocada_em) BETWEEN 18 AND 23 THEN 'Noite (18h-24h)'
                ELSE 'Madrugada (0h-6h)'
            END AS faixa_horario,
            COUNT(*) AS numero_de_escutas
        FROM recently_played
        GROUP BY faixa_horario
        ORDER BY numero_de_escutas DESC;
    """)

    engine.dispose()


if __name__ == "__main__":
    main()
