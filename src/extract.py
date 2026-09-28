"""
veridis — extração de dados do Spotify

Puxa os principais dados da sua conta e salva localmente em arquivos JSON,
dentro de data/raw/. Essa é a camada "bruta" do pipeline — depois vamos
tratar/transformar esses dados e, mais pra frente, subir pro S3.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-top-read user-read-recently-played user-library-read"

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def get_spotify_client():
    """Cria e retorna um cliente autenticado do Spotify."""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def save_json(data, filename):
    """Salva um dicionário/lista como JSON dentro de data/raw/."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    filepath = os.path.join(RAW_DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Salvo: {filepath}")


def extract_top_tracks(sp, time_range="medium_term", limit=50):
    """Extrai as top faixas do usuário. Limitado a 50 pela própria API
    (é um cálculo do Spotify, não sua biblioteca completa)."""
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    return results["items"]


def extract_top_artists(sp, time_range="medium_term", limit=50):
    """Extrai os top artistas do usuário. Mesmo limite de 50 da API."""
    results = sp.current_user_top_artists(limit=limit, time_range=time_range)
    return results["items"]


def extract_recently_played(sp, limit=50):
    """Extrai as últimas faixas tocadas. A própria API só guarda
    histórico das últimas 50 reproduções, não dá pra paginar além disso."""
    results = sp.current_user_recently_played(limit=limit)
    return results["items"]


def extract_saved_tracks(sp):
    """Extrai TODAS as músicas curtidas/salvas pelo usuário, usando
    paginação — diferente dos outros endpoints, aqui não existe teto
    da API: sua biblioteca pode ter qualquer quantidade de faixas, então
    percorremos página por página (50 em 50) até acabar."""
    todas_as_faixas = []
    offset = 0
    limit = 50

    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        itens_da_pagina = results["items"]
        todas_as_faixas.extend(itens_da_pagina)

        print(f"  Página em offset={offset}: {len(itens_da_pagina)} faixas (total até agora: {len(todas_as_faixas)})")

        # Se essa página veio com menos itens que o limite pedido,
        # significa que chegamos ao fim da biblioteca
        if len(itens_da_pagina) < limit:
            break

        offset += limit

    return todas_as_faixas


def run_extraction():
    sp = get_spotify_client()
    timestamp = datetime.now().strftime("%Y-%m-%d")

    print("Extraindo top faixas...")
    top_tracks = extract_top_tracks(sp)
    save_json(top_tracks, f"top_tracks_{timestamp}.json")

    print("Extraindo top artistas...")
    top_artists = extract_top_artists(sp)
    save_json(top_artists, f"top_artists_{timestamp}.json")

    print("Extraindo músicas tocadas recentemente...")
    recently_played = extract_recently_played(sp)
    save_json(recently_played, f"recently_played_{timestamp}.json")

    print("Extraindo músicas curtidas (todas, com paginação)...")
    saved_tracks = extract_saved_tracks(sp)
    save_json(saved_tracks, f"saved_tracks_{timestamp}.json")

    print("\nExtração concluída! Confira os arquivos em data/raw/")


if __name__ == "__main__":
    run_extraction()
