import json


class SyncManager:
    playlist_file = "playlists.json"

    def __init__(self) -> None:
        with open(self.playlist_file, "r") as file:
            self.playlists_to_be_synced: list = json.load(file)

    def add_playlist(self, spotify_playlist_id: str, youtube_playlist_id: str, spotify_name: str, youtube_name: str, spotify_link, youtube_link: str):
        load = {
            "spotify_playlist_id": spotify_playlist_id,
            "youtube_playlist_id": youtube_playlist_id,
            "spotify_name": spotify_name,
            "youtube_name": youtube_name,
            "spotify_link": spotify_link,
            "youtube_link": youtube_link
        }

        self.playlists_to_be_synced.append(load)

    def commit(self):
        with open(self.playlist_file, "w") as file:
            json.dump(self.playlists_to_be_synced, file, indent=2)
