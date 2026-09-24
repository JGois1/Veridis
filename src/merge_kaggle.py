"""
veridis — cruzamento com o dataset do Kaggle

Cruza os dados pessoais extraídos do Spotify (data/processed/) com o
dataset público do Kaggle (data/external/) para trazer gênero e audio
features (dançabilidade, energia, valence, etc) — dados que a API do
Spotify restringiu para apps novos.

O cruzamento é feito por nome da faixa + artista, já que os IDs do
Kaggle não correspondem aos IDs da sua conta Spotify.
"""

import os
import re
import glob
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
EXTERNAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "external")

# Colunas do dataset do Kaggle que queremos trazer pro nosso lado
# (o dataset usa "track_genre", não "genre")
COLUNAS_AUDIO_FEATURES = ["danceability", "energy", "valence", "tempo", "acousticness"]


def normalizar(texto):
    """Deixa o texto minúsculo e remove coisas como '- Remaster',
    '(feat. ...)', anos entre parênteses, etc — pra aumentar a chance
    de encontrar a mesma música em bases diferentes."""
    if pd.isna(texto):
        return ""
    texto = texto.lower().strip()
    texto = re.sub(r"\s*-\s*.*(remaster|version|edit|mix).*", "", texto)
    texto = re.sub(r"\s*\(feat\..*?\)", "", texto)
    texto = re.sub(r"\s*\(.*?\)", "", texto)
    return texto.strip()


def carregar_dataset_kaggle():
    """Encontra e carrega o CSV do Kaggle, normaliza os campos de
    cruzamento e agrupa faixas duplicadas (o Kaggle repete a mesma
    música uma vez por gênero em que ela se encaixa)."""
    arquivos = glob.glob(os.path.join(EXTERNAL_DIR, "*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            "Nenhum CSV encontrado em data/external/. Baixe o dataset do Kaggle primeiro."
        )
    df = pd.read_csv(arquivos[0])

    df["nome_faixa_norm"] = df["track_name"].apply(normalizar)
    # O Kaggle junta múltiplos artistas com ";" (ex: "Charlie Puth;Selena Gomez").
    # Pegamos só o primeiro, pra bater com o formato dos nossos dados pessoais
    # (que também só guardam o artista principal da faixa).
    df["artista_norm"] = df["artists"].apply(lambda x: normalizar(str(x).split(";")[0]))

    # O Kaggle tem uma linha por gênero em que a faixa se encaixa (a mesma
    # música pode aparecer várias vezes, uma por gênero). Agrupamos por
    # faixa+artista, juntando todos os gêneros numa lista só, e mantendo
    # o primeiro valor de audio features (que se repete em cada linha).
    agregacoes = {"track_genre": lambda generos: ", ".join(sorted(set(generos)))}
    agregacoes.update({coluna: "first" for coluna in COLUNAS_AUDIO_FEATURES})

    df_agrupado = df.groupby(["nome_faixa_norm", "artista_norm"]).agg(agregacoes).reset_index()
    return df_agrupado


def enriquecer_top_tracks():
    """Cruza o top_tracks.csv pessoal com o dataset do Kaggle já agrupado."""
    caminho_top_tracks = os.path.join(PROCESSED_DIR, "top_tracks.csv")
    df_pessoal = pd.read_csv(caminho_top_tracks)
    df_kaggle = carregar_dataset_kaggle()

    df_pessoal["nome_faixa_norm"] = df_pessoal["nome_faixa"].apply(normalizar)
    df_pessoal["artista_norm"] = df_pessoal["artista"].apply(normalizar)

    # merge = "junção" de tabelas, o equivalente do pandas a um JOIN em SQL
    df_resultado = df_pessoal.merge(
        df_kaggle,
        on=["nome_faixa_norm", "artista_norm"],
        how="left",  # mantém todas as suas faixas, mesmo as que não encontrarem par
    )

    # Limpa as colunas auxiliares de normalização, não precisamos delas no resultado final
    df_resultado = df_resultado.drop(columns=["nome_faixa_norm", "artista_norm"])

    return df_resultado


def run_enrichment():
    print("Cruzando seus dados com o dataset do Kaggle...\n")
    df_resultado = enriquecer_top_tracks()

    total = len(df_resultado)
    encontrados = df_resultado["track_genre"].notna().sum()
    print(f"Faixas encontradas no Kaggle: {encontrados} de {total} ({encontrados/total:.0%})\n")

    output_path = os.path.join(PROCESSED_DIR, "top_tracks_enriquecido.csv")
    df_resultado.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Salvo: {output_path}")


if __name__ == "__main__":
    run_enrichment()
