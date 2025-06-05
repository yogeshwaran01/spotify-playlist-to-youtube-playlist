import os
import json

from pytube import Search
from pytube.contrib.search import logger

from google_auth_oauthlib.flow import Flow  # Changed from InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth.transport.requests # Required for flow.fetch_token

logger.disabled = True

# Placeholder for the path to the client secret file
# This should be configured via environment variable or a fixed path
# For this subtask, we'll assume it's in the backend directory
CLIENT_SECRET_FILE_PATH = os.path.join(os.path.dirname(__file__), 'youtube_client_secret.json')

def get_google_auth_url(redirect_uri: str, scopes: list[str], state: str = None) -> str | None:
    """Generates the Google OAuth 2.0 authorization URL."""
    if not os.path.exists(CLIENT_SECRET_FILE_PATH):
        print(f"Error: YouTube client secret file not found at {CLIENT_SECRET_FILE_PATH}")
        # In a real app, you might raise an exception or handle this more gracefully
        return None

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE_PATH,
        scopes=scopes,
        state=state
    )
    flow.redirect_uri = redirect_uri
    # access_type='offline' to get a refresh token
    # prompt='consent' to ensure the user is prompted, good for dev to get refresh tokens
    authorization_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
    return authorization_url

def exchange_google_code_for_credentials(redirect_uri: str, scopes: list[str], code: str) -> Credentials | None:
    """Exchanges an authorization code for Google OAuth 2.0 credentials."""
    if not os.path.exists(CLIENT_SECRET_FILE_PATH):
        print(f"Error: YouTube client secret file not found at {CLIENT_SECRET_FILE_PATH}")
        return None

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE_PATH,
        scopes=scopes
    )
    flow.redirect_uri = redirect_uri

    try:
        # Use a Request object from google.auth.transport.requests to ensure proper token fetching
        request_session = google.auth.transport.requests.Request()
        flow.fetch_token(code=code, request_session=request_session)
        return flow.credentials
    except Exception as e:
        print(f"Error exchanging code for Google credentials: {e}")
        return None

def credentials_to_dict(credentials: Credentials) -> dict:
    """Converts Google OAuth2 credentials object to a dictionary."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'id_token': getattr(credentials, 'id_token', None), # if OIDC scopes were used
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
    }

def credentials_from_dict(creds_dict: dict) -> Credentials:
    """Creates Google OAuth2 credentials object from a dictionary."""
    return Credentials(
        token=creds_dict.get('token'),
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict.get('token_uri'),
        client_id=creds_dict.get('client_id'),
        client_secret=creds_dict.get('client_secret'),
        scopes=creds_dict.get('scopes')
        # Expiry is handled by the Credentials object itself if token is expired and refresh_token is present
    )

class YouTubeClient:
    def __init__(self, credentials_dict: dict = None):
        self.youtube = None
        if credentials_dict:
            creds = credentials_from_dict(credentials_dict)
            # Check if credentials have expired and refresh if necessary
            # This requires a google.auth.transport.requests.Request object
            if creds and creds.expired and creds.refresh_token:
                try:
                    request_session = google.auth.transport.requests.Request()
                    creds.refresh(request_session)
                    # Potentially save the refreshed credentials back to session - handled in app.py
                except Exception as e:
                    print(f"Error refreshing YouTube credentials: {e}")
                    # Handle inability to refresh, e.g., by clearing credentials or requiring re-login
                    self.youtube = None
                    return

            if creds and creds.valid:
                 self.youtube = build("youtube", "v3", credentials=creds)
            else:
                print("Warning: YouTubeClient initialized with invalid or missing credentials.")
        else:
            # Optionally, allow initialization without credentials for non-authenticated calls (if any)
            # Or raise an error if credentials are always required.
            print("Warning: YouTubeClient initialized without credentials.")

    # Ensure self.youtube is checked before use in other methods
    def create_playlist(
        self, name: str, description: str, privacy_status: str = "private"
    ):
        if not self.youtube:
            raise Exception("YouTube client not authenticated.")
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
                    "status": {"privacyStatus": privacy_status},
                },
            )
            .execute()
        )
        # Return the ID of the newly created playlist
        return playlist.get('id') if playlist else None

    # This is the more complete add_song_playlist method from the end of the file, keep this one.
    # The earlier one with the same name should be removed by this replacement.
    def add_track_to_playlist(self, youtube_playlist_id: str, youtube_video_id: str) -> bool:
        if not self.youtube:
            print("Error: YouTube client not authenticated.")
            return False
        try:
            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": youtube_playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": youtube_video_id},
                    }
                },
            ).execute()
            return True
        except Exception as e:
            print(f"Error adding track {youtube_video_id} to playlist {youtube_playlist_id}: {e}")
            return False

    def remove_song_playlist(self, playlist_id: str, video_id: str): # video_id here should be playlist_item_id
        if not self.youtube:
            raise Exception("YouTube client not authenticated.")
        # Note: The original implementation for remove_song_playlist seems incorrect.
        # It should use playlistItemId, not video_id directly in delete.
        # This is a pre-existing issue, not introduced by this change.
        # For now, keeping the logic but adding the auth check.
        # A proper fix would involve finding the playlistItemId for the video_id in that playlist.
        request = self.youtube.playlistItems().delete(id=video_id) # This 'id' should be playlistItemId
        response = request.execute()
        return response

    def search_track(self, query: str, max_results: int = 1) -> str | None:
        if not self.youtube:
            print("Error: YouTube client not authenticated.")
            return None
        try:
            search_response = self.youtube.search().list(
                q=query,
                part="snippet",
                maxResults=max_results,
                type="video"
            ).execute()

            if search_response.get("items"):
                return search_response["items"][0]["id"]["videoId"]
            else:
                print(f"No YouTube video found for query: {query}")
                return None
        except Exception as e:
            print(f"Error searching YouTube for track '{query}': {e}")
            return None

    def get_playlist(self, playlist_id):
        if not self.youtube:
            raise Exception("YouTube client not authenticated.")
        videos = []
        next_page_token = None

        while True:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )

            response = request.execute()

            videos.extend(response["items"])
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return videos
