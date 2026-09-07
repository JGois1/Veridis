"""
veridis — playground de exploração da API do Spotify

Esse arquivo é um espaço livre pra testar endpoints e brincar com os dados, sem misturar
com os scripts do pipeline (auth_test.py, extract.py, etc).
Nada aqui é salvo — é só pra visualizar na tela e aprender.
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-top-read user-read-recently-played user-library-read"


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
    while True:
        print("\nO que você quer ver?")
        print("1 - Top faixas")
        print("2 - Top artistas")
        print("3 - Tocadas recentemente")
        print("4 - Músicas curtidas")
        print("0 - Sair")

        escolha = input("Digite o número: ")

        sp = get_spotify_client()

        if escolha == "1":
            print_top_tracks(sp)
        elif escolha == "2":
            print_top_artists(sp)
        elif escolha == "3":
            print_recently_played(sp)
        elif escolha == "4":
            print_saved_tracks(sp)
        elif escolha == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida, tenta de novo.")


if __name__ == "__main__":
    menu()
