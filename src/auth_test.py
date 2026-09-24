"""
veridis — teste de autenticação com a API do Spotify

Esse script serve só pra confirmar que a autenticação está funcionando.
Ele vai abrir o navegador, pedir pra você logar no Spotify e autorizar o app,
e depois imprimir suas top 5 faixas mais escutadas recentemente.
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-top-read"


def get_spotify_client():
    """Cria e retorna um cliente autenticado do Spotify."""
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def test_connection():
    """Testa a conexão buscando as top 5 faixas do usuário."""
    sp = get_spotify_client()

    print("\nConectado com sucesso! Buscando suas top faixas...\n")

    results = sp.current_user_top_tracks(limit=5, time_range="short_term")

    for i, item in enumerate(results["items"], start=1):
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]
        print(f"{i}. {track_name} — {artist_name}")


if __name__ == "__main__":
    test_connection()
