import os
from dataclasses import dataclass
from urllib.parse import urlencode

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import dotenv
import requests # Added for exchanging code for token

dotenv.load_dotenv()


# Spotify OAuth URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


def get_spotify_auth_url(client_id: str, redirect_uri: str, scope: str, state: str = None) -> str:
    """Generates the Spotify authorization URL."""
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    if state:
        params["state"] = state
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"


def exchange_spotify_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict | None:
    """Exchanges an authorization code for an access token."""
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # Log error or handle it appropriately
        print(f"Error exchanging code for token: {response.status_code} - {response.text}")
        return None


@dataclass
class Playlist:
    name: str
    description: str
    tracks: list[str]


class SpotifyClient:
    # Accepts token_info dictionary from session or just an auth_token string
    def __init__(self, token_info: dict = None, auth_token: str = None) -> None:
        self.sp = None
        access_token = None

        if token_info and isinstance(token_info, dict):
            access_token = token_info.get('access_token')
        elif auth_token: # Fallback for direct token string
            access_token = auth_token

        if access_token:
            self.sp = spotipy.Spotify(auth=access_token)
            # To handle token refresh with Spotipy, you'd typically initialize with SpotifyOAuth:
            # self.oauth_manager = spotipy.SpotifyOAuth(
            #     client_id=os.getenv("SPOTIFY_CLIENT_ID"), # Ensure these are available
            #     client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            #     redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            #     scope=token_info.get('scope'), # Make sure scope is in token_info or passed
            #     cache_path=None, # Don't use file cache for server
            #     token_info=token_info # Pass the whole token_info
            # )
            # self.sp = spotipy.Spotify(oauth_manager=self.oauth_manager)
            # However, SPOTIPY_CLIENT_ID etc. env vars must be set for SpotifyOAuth.
            # For now, direct access token usage. Manual refresh would be needed if it expires.
        else:
            # Fallback to client credentials for non-user-specific calls (if any)
            client_id = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET")
            if client_id != "YOUR_SPOTIFY_CLIENT_ID" and client_secret != "YOUR_SPOTIFY_CLIENT_SECRET":
                auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
            else:
                print("Warning: SpotifyClient initialized without user auth token or app client credentials.")

    def get_user_playlists(self):
        if not self.sp:
            return None, "Client not authenticated or initialized properly"
        try:
            results = self.sp.current_user_playlists(limit=50)
            playlists = []
            if results and results.get('items'):
                for item in results['items']:
                    playlists.append({
                        'id': item['id'],
                        'name': item['name'],
                        'owner': item['owner']['display_name'] if item.get('owner') else 'Unknown',
                        'tracks_total': item['tracks']['total'] if item.get('tracks') else 0
                    })
            return playlists, None
        except spotipy.SpotifyException as e:
            # Handle specific Spotipy exceptions, e.g., for auth errors
            if e.http_status == 401: # Unauthorized
                 # This could mean the token is expired or invalid
                 # The app.py route should handle this, possibly by asking user to re-login
                 # or attempting a refresh if refresh_token is available and managed.
                return None, f"Spotify API_error_401: {e.msg}"
            return None, f"Spotify API error: {str(e)}"
        except Exception as e:
            print(f"Error fetching user playlists: {e}") # Log this
            return None, str(e)

    def get_playlist_tracks(self, playlist_id: str) -> tuple[list[dict] | None, str | None]:
        if not self.sp:
            return None, "Client not authenticated or initialized properly"

        tracks = []
        try:
            results = self.sp.playlist_items(playlist_id)
            if results:
                for item in results['items']:
                    track = item.get('track')
                    if track and track.get('name') and track.get('artists'):
                        tracks.append({
                            'name': track['name'],
                            'artist': track['artists'][0]['name'] # Taking the primary artist
                        })
                # Handle pagination if there are more than 100 tracks (default limit for playlist_items)
                while results and results['next']:
                    results = self.sp.next(results)
                    for item in results['items']:
                        track = item.get('track')
                        if track and track.get('name') and track.get('artists'):
                            tracks.append({
                                'name': track['name'],
                                'artist': track['artists'][0]['name']
                            })
            return tracks, None
        except spotipy.SpotifyException as e:
            if e.http_status == 401:
                return None, f"Spotify API_error_401: {e.msg}" # Token expired or invalid
            return None, f"Spotify API error while fetching playlist tracks: {str(e)}"
        except Exception as e:
            print(f"Error fetching playlist tracks for {playlist_id}: {e}") # Log this
            return None, str(e)

    def get_playlist(self, id: str): # This method seems to return a custom Playlist object, not just tracks
        if not self.sp:
            raise Exception("SpotifyClient not initialized properly.")
        playlist = self.sp.playlist(id)
        queries = []
        tracks = playlist["tracks"]["items"]
        for track in tracks:
            track_name = track["track"]["name"]
            artists = ", ".join(
                [artist["name"] for artist in track["track"]["artists"]]
            )
            queries.append(f"{track_name} by {artists}")
        return Playlist(playlist["name"], playlist["description"], queries)
