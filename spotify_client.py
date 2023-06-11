import os
from dataclasses import dataclass

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import dotenv

dotenv.load_dotenv()


@dataclass
class Playlist:
    name: str
    description: str
    tracks: list[str]


class SpotifyClient:
    def __init__(self) -> None:
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        auth_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlist(self, id: str):
        playlist = self.spotify.playlist(id)
        queries = []
        tracks = playlist["tracks"]["items"]
        for track in tracks:
            track_name = track["track"]["name"]
            artists = ", ".join(
                [artist["name"] for artist in track["track"]["artists"]]
            )
            queries.append(f"{track_name} by {artists}")
        return Playlist(playlist["name"], playlist["description"], queries)
