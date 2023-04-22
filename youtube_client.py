from pytube import Search
from pytube.contrib.search import logger

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger.disabled = True

class YouTubeClient:
    def __init__(self) -> None:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
        )

        creds = flow.run_local_server()

        self.youtube = build("youtube", "v3", credentials=creds)

    def create_playlist(self, name: str, description: str):
        playlist = (
            self.youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": name,
                        "description": description,
                        "defaultLanguage": "en",
                    },
                    "status": {"privacyStatus": "public"},
                },
            )
            .execute()
        )

        return playlist

    def add_song_playlist(self, playlist_id: str, video_id: str):
        request = (
                self.youtube.playlistItems()
                .insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": video_id},
                        }
                    },
                )
            )
        playlist_item = request.execute()
        return playlist_item

    def search_video(self, query: str):

        return Search(query).results[0].video_id