import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
from spotify_client import SpotifyClient
from youtube_client import YouTubeClient
from sync_manager import SyncManager

PORT = 8000
WEB_DIR = 'web'

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_POST(self):
        if self.path == '/create':
            self.handle_create()
        elif self.path == '/sync':
            self.handle_sync()
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def handle_create(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        spotify_playlist_id = data.get('spotify_playlist_id')
        name = data.get('name')
        description = data.get('description')
        privacy = data.get('privacy')

        try:
            spotify = SpotifyClient()
            youtube = YouTubeClient()
            spotify_playlist = spotify.get_playlist(spotify_playlist_id)

            if not name:
                name = spotify_playlist.name
            if not description:
                description = spotify_playlist.description

            youtube_playlist = youtube.create_playlist(name, description, privacy_status=privacy)
            youtube_playlist_id = youtube_playlist['id']

            for track in spotify_playlist.tracks:
                video = youtube.search_video(track)
                youtube.add_song_playlist(youtube_playlist_id, video.video_id)

            playlist_url = f"https://www.youtube.com/playlist?list={youtube_playlist_id}"
            response = {'playlist_url': playlist_url}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_sync(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        spotify_playlist_id = data.get('spotify_playlist_id')
        youtube_playlist_id = data.get('youtube_playlist_id')

        try:
            spotify = SpotifyClient()
            youtube = YouTubeClient()

            spotify_playlist = spotify.get_playlist(spotify_playlist_id)
            youtube_playlist = youtube.get_playlist(youtube_playlist_id)
            youtube_playlist_ids = [item['snippet']['resourceId']['videoId'] for item in youtube_playlist]

            searched_playlist = [youtube.search_video(track).video_id for track in spotify_playlist.tracks]

            songs_to_be_added = [song for song in searched_playlist if song not in youtube_playlist_ids]
            songs_to_be_removed = [item['id'] for item in youtube_playlist if item['snippet']['resourceId']['videoId'] not in searched_playlist]

            for song in songs_to_be_added:
                youtube.add_song_playlist(youtube_playlist_id, song)
            for song in songs_to_be_removed:
                youtube.remove_song_playlist(youtube_playlist_id, song)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

def run_server():
    with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
