"""
veridis — transformação dos dados do Spotify

Lê os arquivos JSON brutos (em data/raw/), extrai só os campos que
interessam pra análise, limpa e organiza em tabelas, e salva como CSV
em data/processed/ — prontos para virar tabelas SQL na próxima etapa.

Nota: usei .get() em vez de [] em vários campos porque o Spotify
restringiu alguns campos (como "popularity" e "genres") para apps
criados recentemente. Com .get(), se o campo não vier na resposta,
usamos um valor padrão em vez de o script quebrar.
"""

import os
import glob
import json
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

VALOR_PADRAO = "indisponível"


def load_latest_json(prefix):
    """Encontra e carrega o arquivo JSON mais recente que começa com o
    prefixo dado (ex: 'top_tracks' encontra 'top_tracks_2026-09-03.json')."""
    pattern = os.path.join(RAW_DATA_DIR, f"{prefix}_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Nenhum arquivo encontrado para '{prefix}' em data/raw/")
    latest_file = files[-1]
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_top_tracks(raw_data):
    """Extrai campos relevantes das top faixas."""
    rows = []
    for i, track in enumerate(raw_data, start=1):
        rows.append({
            "ranking": i,
            "nome_faixa": track.get("name", VALOR_PADRAO),
            "artista": track["artists"][0].get("name", VALOR_PADRAO) if track.get("artists") else VALOR_PADRAO,
            "album": track.get("album", {}).get("name", VALOR_PADRAO),
            "popularidade": track.get("popularity", VALOR_PADRAO),
            "duracao_ms": track.get("duration_ms", VALOR_PADRAO),
            "duracao_min": round(track["duration_ms"] / 60000, 2) if track.get("duration_ms") else VALOR_PADRAO,
            "data_lancamento": track.get("album", {}).get("release_date", VALOR_PADRAO),
            "spotify_id": track.get("id", VALOR_PADRAO),
        })
    return pd.DataFrame(rows)


def transform_top_artists(raw_data):
    """Extrai campos relevantes dos top artistas."""
    rows = []
    for i, artist in enumerate(raw_data, start=1):
        generos = artist.get("genres")
        rows.append({
            "ranking": i,
            "nome_artista": artist.get("name", VALOR_PADRAO),
            "generos": ", ".join(generos) if generos else "não informado",
            "popularidade": artist.get("popularity", VALOR_PADRAO),
            "seguidores": artist.get("followers", {}).get("total", VALOR_PADRAO),
            "spotify_id": artist.get("id", VALOR_PADRAO),
        })
    return pd.DataFrame(rows)


def transform_recently_played(raw_data):
    """Extrai campos relevantes das músicas tocadas recentemente."""
    rows = []
    for item in raw_data:
        track = item.get("track", {})
        rows.append({
            "nome_faixa": track.get("name", VALOR_PADRAO),
            "artista": track["artists"][0].get("name", VALOR_PADRAO) if track.get("artists") else VALOR_PADRAO,
            "album": track.get("album", {}).get("name", VALOR_PADRAO),
            "tocada_em": item.get("played_at"),
            "spotify_id": track.get("id", VALOR_PADRAO),
        })
    df = pd.DataFrame(rows)
    df["tocada_em"] = pd.to_datetime(df["tocada_em"])
    return df


def transform_saved_tracks(raw_data):
    """Extrai campos relevantes das músicas curtidas/salvas."""
    rows = []
    for item in raw_data:
        track = item.get("track", {})
        rows.append({
            "nome_faixa": track.get("name", VALOR_PADRAO),
            "artista": track["artists"][0].get("name", VALOR_PADRAO) if track.get("artists") else VALOR_PADRAO,
            "album": track.get("album", {}).get("name", VALOR_PADRAO),
            "popularidade": track.get("popularity", VALOR_PADRAO),
            "curtida_em": item.get("added_at"),
            "spotify_id": track.get("id", VALOR_PADRAO),
        })
    df = pd.DataFrame(rows)
    df["curtida_em"] = pd.to_datetime(df["curtida_em"])
    return df


def save_csv(df, filename):
    """Salva um DataFrame como CSV em data/processed/."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"  Salvo: {filepath} ({len(df)} linhas)")


def run_transformation():
    print("Transformando top faixas...")
    df_top_tracks = transform_top_tracks(load_latest_json("top_tracks"))
    save_csv(df_top_tracks, "top_tracks.csv")

    print("Transformando top artistas...")
    df_top_artists = transform_top_artists(load_latest_json("top_artists"))
    save_csv(df_top_artists, "top_artists.csv")

    print("Transformando músicas tocadas recentemente...")
    df_recently_played = transform_recently_played(load_latest_json("recently_played"))
    save_csv(df_recently_played, "recently_played.csv")

    print("Transformando músicas curtidas...")
    df_saved_tracks = transform_saved_tracks(load_latest_json("saved_tracks"))
    save_csv(df_saved_tracks, "saved_tracks.csv")

    print("\nTransformação concluída! Confira os arquivos em data/processed/")


if __name__ == "__main__":
    run_transformation()
