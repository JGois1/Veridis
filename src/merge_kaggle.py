"""
veridis — cruzamento com o dataset do Kaggle

Cruza os dados pessoais extraídos do Spotify (data/processed/) com o
dataset público do Kaggle (data/external/) para trazer gênero e audio
features (dançabilidade, energia, valence, etc) — dados que a API do
Spotify restringiu para apps novos.

O cruzamento é feito por nome da faixa + artista, já que os IDs do
Kaggle não correspondem aos IDs da sua conta Spotify. É aplicado tanto
nas top faixas quanto nas músicas curtidas (a base maior, com toda a
biblioteca).
"""

import os
import re
import glob
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
EXTERNAL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "external")

# Colunas de audio features do dataset do Kaggle que queremos trazer pro nosso lado
COLUNAS_AUDIO_FEATURES = ["danceability", "energy", "valence", "tempo", "acousticness"]

# Tabelas pessoais que serão enriquecidas: (arquivo de entrada, arquivo de saída)
TABELAS_PARA_ENRIQUECER = [
    ("top_tracks.csv", "top_tracks_enriquecido.csv"),
    ("saved_tracks.csv", "saved_tracks_enriquecido.csv"),
]


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

    # O Kaggle tem uma linha por gênero em que a faixa se encaixa. Agrupamos
    # por faixa+artista, juntando todos os gêneros numa lista só, e mantendo
    # o primeiro valor de audio features (que se repete em cada linha).
    agregacoes = {"track_genre": lambda generos: ", ".join(sorted(set(generos)))}
    agregacoes.update({coluna: "first" for coluna in COLUNAS_AUDIO_FEATURES})

    df_agrupado = df.groupby(["nome_faixa_norm", "artista_norm"]).agg(agregacoes).reset_index()
    return df_agrupado


def enriquecer_tabela(df_kaggle, arquivo_entrada, arquivo_saida):
    """Cruza uma tabela pessoal (CSV em data/processed/) com o dataset do
    Kaggle já agrupado e salva o resultado como um novo CSV."""
    df_pessoal = pd.read_csv(os.path.join(PROCESSED_DIR, arquivo_entrada))

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

    total = len(df_resultado)
    encontrados = df_resultado["track_genre"].notna().sum()
    print(f"  {arquivo_entrada}: {encontrados} de {total} faixas encontradas no Kaggle ({encontrados/total:.0%})")

    caminho_saida = os.path.join(PROCESSED_DIR, arquivo_saida)
    df_resultado.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(f"  Salvo: {caminho_saida}\n")


def run_enrichment():
    print("Cruzando seus dados com o dataset do Kaggle...\n")
    df_kaggle = carregar_dataset_kaggle()

    for arquivo_entrada, arquivo_saida in TABELAS_PARA_ENRIQUECER:
        enriquecer_tabela(df_kaggle, arquivo_entrada, arquivo_saida)


if __name__ == "__main__":
    run_enrichment()
