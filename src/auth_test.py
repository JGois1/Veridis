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

# Carrega as variáveis do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Escopo = quais permissões estamos pedindo ao usuário
# user-top-read: acesso às faixas/artistas mais ouvidos
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

def print_top_tracks(sp):
    results = sp.current_user_top_tracks(limit=50)
    for i, item in enumerate(results["items"], start=1):
        track_name = item["name"]
        print(f"{i}. {track_name}")


def print_top_artists(sp):
    results = sp.current_user_top_artists(limit=50)
    for i, item in enumerate(results["items"], start=1):
        artist_name = item["name"]
        print(f"{i}. {artist_name}")

def print_recently_played(sp):
    results = sp.current_user_recently_played(limit=50)
    for i, item in enumerate(results["items"], start=1):
        track_name = item["track"]["name"]
        print(f"{i}. {track_name}")

def print_saved_tracks(sp):
    results = sp.current_user_saved_tracks(limit=50)
    for i, item in enumerate(results["items"], start=1):
        track_name = item["track"]["name"]
        print(f"{i}. {track_name}")

def menu():
    print("\nO que você quer ver?")
    print("1 - Top faixas")
    print("2 - Top artistas")
    print("3 - Tocadas recentemente")
    print("4 - Músicas curtidas")
    print("0 - Sair")

    escolha = input("Digite o número: ")

    sp = get_spotify_client()

    match escolha:
        case "1":
            print_top_tracks(sp)
        case "2":
            print_top_artists(sp)
        case "3":
            print_recently_played(sp)
        case "4":
            print_saved_tracks(sp)
        case "0":
            print("Até mais!")
        case _:
            print("Opção inválida, tenta de novo.")

if __name__ == "__main__":
    menu()
