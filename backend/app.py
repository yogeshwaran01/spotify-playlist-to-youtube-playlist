from flask import Flask, jsonify, session, redirect, request
import os
from flask_cors import CORS # Import CORS
# Assuming spotify_client is in the same directory or accessible via PYTHONPATH
from spotify_client import get_spotify_auth_url, exchange_spotify_code_for_token, SpotifyClient
# Import YouTube client functions
from youtube_client import get_google_auth_url, exchange_google_code_for_credentials, credentials_to_dict, credentials_from_dict, YouTubeClient
from sync_manager import SyncManager # Import SyncManager

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key') # Replace with a strong secret key
CORS(app) # Initialize CORS for the app, allowing all origins by default.
          # For production, configure origins: CORS(app, origins=["http://localhost:4200"])

# YouTube OAuth Configuration
# YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "YOUR_YOUTUBE_CLIENT_ID.apps.googleusercontent.com")
# YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "YOUR_YOUTUBE_CLIENT_SECRET")
# These are now primarily managed by youtube_client_secret.json
YOUTUBE_REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI", "http://localhost:5000/auth/youtube/callback")
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtubepartner"]


@app.route('/auth/youtube/login', methods=['GET'])
def youtube_login():
    # Optional: Add 'state' for CSRF protection
    # state = os.urandom(16).hex()
    # session['youtube_auth_state'] = state
    auth_url = get_google_auth_url(YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES) #, state=state)
    if auth_url:
        return redirect(auth_url)
    else:
        return jsonify({"message": "Error generating YouTube auth URL. Check server logs."}), 500

@app.route('/auth/youtube/callback', methods=['GET'])
def youtube_callback():
    code = request.args.get('code')
    # received_state = request.args.get('state') # Optional
    # saved_state = session.pop('youtube_auth_state', None) # Optional

    # Optional: CSRF protection check
    # if not saved_state or saved_state != received_state:
    #     return jsonify({"message": "State mismatch error or missing state."}), 400

    if not code:
        return jsonify({"message": "Authorization code not found in callback."}), 400

    credentials = exchange_google_code_for_credentials(YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES, code)

    if credentials:
        session['youtube_credentials'] = credentials_to_dict(credentials)
        return jsonify({"message": "YouTube authentication successful"}) # Redirect to frontend in a real app
    else:
        return jsonify({"message": "YouTube authentication failed: Could not exchange code for credentials"}), 400

@app.route('/auth/spotify/login', methods=['GET'])
def spotify_login():
    # Placeholders for Spotify credentials and settings
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
    SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:5000/auth/spotify/callback")
    SPOTIFY_SCOPE = "playlist-read-private playlist-modify-public playlist-modify-private user-library-read"
    # Optional: Add 'state' for CSRF protection
    # state = os.urandom(16).hex()
    # session['spotify_auth_state'] = state

    auth_url = get_spotify_auth_url(SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPE) #, state=state)
    return redirect(auth_url)

@app.route('/auth/spotify/callback', methods=['GET'])
def spotify_callback():
    code = request.args.get('code')
    # received_state = request.args.get('state') # Optional
    # saved_state = session.pop('spotify_auth_state', None) # Optional

    # Optional: CSRF protection check
    # if not saved_state or saved_state != received_state:
    #     return jsonify({"message": "State mismatch error or missing state."}), 400

    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "YOUR_SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "YOUR_SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:5000/auth/spotify/callback")

    if not code:
        return jsonify({"message": "Authorization code not found in callback."}), 400

    token_info = exchange_spotify_code_for_token(code, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI)

    if token_info:
        session['spotify_token_info'] = token_info  # This includes access_token, refresh_token, expires_in, etc.
        # You might want to calculate the actual expiry timestamp here:
        # session['spotify_token_expires_at'] = time.time() + token_info['expires_in']
        return jsonify({"message": "Spotify authentication successful", "token_info": token_info}) # Redirect to frontend in a real app
    else:
        return jsonify({"message": "Spotify authentication failed: Could not exchange code for token"}), 400

# Example of how to use the YouTube client with refreshed credentials
@app.route('/api/youtube/playlists', methods=['GET']) # Example route
def youtube_playlists_example():
    creds_dict = session.get('youtube_credentials')
    if not creds_dict:
        return jsonify({"message": "User not authenticated with YouTube."}), 401

    # The YouTubeClient's __init__ will attempt to refresh if necessary
    yt_client = YouTubeClient(credentials_dict=creds_dict)

    # If refresh occurred, new token might be available in yt_client.youtube.credentials
    # It's good practice to update the session if credentials were refreshed.
    if yt_client.youtube and yt_client.youtube.credentials and yt_client.youtube.credentials.valid:
        # Check if token was refreshed by comparing with original or checking expiry
        # For simplicity, always update if valid after potential refresh attempt
        # A more robust check would compare tokens or expiry if available before refresh
        updated_creds_dict = credentials_to_dict(yt_client.youtube.credentials)
        if updated_creds_dict.get('token') != creds_dict.get('token'): # Basic check if token changed
             session['youtube_credentials'] = updated_creds_dict


    if not yt_client.youtube:
        # This means authentication or refresh failed
        session.pop('youtube_credentials', None) # Clear invalid credentials
        return jsonify({"message": "Failed to initialize YouTube client or refresh credentials. Please re-authenticate."}), 500

    try:
        # Example: Get user's playlists (requires appropriate scope)
        # This part is just an example, actual method might differ
        # playlists_response = yt_client.youtube.playlists().list(part="snippet", mine=True).execute()
        # return jsonify(playlists_response)
        return jsonify({"message": "YouTube client initialized, example playlist call commented out."})

    except Exception as e:
        return jsonify({"message": f"Error fetching YouTube playlists: {str(e)}"}), 500


@app.route('/api/spotify/playlists', methods=['GET'])
def spotify_playlists():
    token_info = session.get('spotify_token_info')
    if not token_info:
        return jsonify({"error": "User not authenticated with Spotify"}), 401

    # The SpotifyClient is initialized with the token_info from the session
    spotify_client = SpotifyClient(token_info=token_info)

    if not spotify_client.sp:
        # This case might happen if token_info was present but invalid for Spotipy init
        return jsonify({"error": "Failed to initialize Spotify client. Invalid token?"}), 500

    playlists_data, error = spotify_client.get_user_playlists()

    if error:
        if "API_error_401" in error: # Specific handling for 401 from our client
            # Potentially try to refresh token here if refresh logic was part of SpotifyClient or app route
            # For now, assume re-authentication is needed
            session.pop('spotify_token_info', None) # Clear potentially invalid token
            return jsonify({"error": "Spotify token expired or invalid. Please re-authenticate.", "details": error}), 401
        return jsonify({"error": "Failed to fetch Spotify playlists", "details": error}), 500

    return jsonify(playlists_data)

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body, JSON expected."}), 400

    spotify_playlist_id = data.get('spotify_playlist_id')
    youtube_playlist_name = data.get('youtube_playlist_name')

    if not spotify_playlist_id or not youtube_playlist_name:
        return jsonify({"error": "Missing 'spotify_playlist_id' or 'youtube_playlist_name' in request."}), 400

    # Check for Spotify credentials
    spotify_token_info = session.get('spotify_token_info')
    if not spotify_token_info:
        return jsonify({"error": "User not authenticated with Spotify."}), 401

    # Check for YouTube credentials
    youtube_creds_dict = session.get('youtube_credentials')
    if not youtube_creds_dict:
        return jsonify({"error": "User not authenticated with YouTube."}), 401

    try:
        # Instantiate clients
        spotify_client = SpotifyClient(token_info=spotify_token_info)
        if not spotify_client.sp: # Check if Spotipy client initialized correctly
             # This could happen if token is invalid right from the start
            session.pop('spotify_token_info', None)
            return jsonify({"error": "Failed to initialize Spotify client with stored token. Please re-authenticate with Spotify."}), 401

        youtube_client = YouTubeClient(credentials_dict=youtube_creds_dict)
        if not youtube_client.youtube: # Check if YouTube client initialized correctly
            session.pop('youtube_credentials', None)
            return jsonify({"error": "Failed to initialize YouTube client with stored credentials. Please re-authenticate with YouTube."}), 401

        # Handle YouTube credential refresh: if the client refreshed them, update session
        if youtube_client.youtube.credentials and youtube_client.youtube.credentials.valid:
            updated_youtube_creds = credentials_to_dict(youtube_client.youtube.credentials)
            if updated_youtube_creds.get('token') != youtube_creds_dict.get('token'):
                session['youtube_credentials'] = updated_youtube_creds

        # Instantiate SyncManager
        sync_manager = SyncManager(spotify_client=spotify_client, youtube_client=youtube_client)

        # Perform conversion
        conversion_result = sync_manager.convert_playlist(spotify_playlist_id, youtube_playlist_name)

        return jsonify(conversion_result)

    except ValueError as ve: # Catch initialization errors from SyncManager
        return jsonify({"error": f"Client initialization failed: {str(ve)}"}), 500
    except Exception as e:
        # Log the exception e
        print(f"An unexpected error occurred during conversion: {e}")
        return jsonify({"error": "An unexpected error occurred during playlist conversion.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
