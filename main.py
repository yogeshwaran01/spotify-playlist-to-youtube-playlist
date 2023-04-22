import sys
import time
from spotify_client import SpotifyClient
from youtube_client import YouTubeClient

spotify = SpotifyClient()
youtube = YouTubeClient()

spotify_playlist_id = sys.argv[1]

spotify_playlist = spotify.get_playlist(spotify_playlist_id)

youtube_playlist_id = youtube.create_playlist(spotify_playlist.name, spotify_playlist.description)['id']


for track in spotify_playlist.tracks:
    print(f"Searching for {track}")
    id = youtube.search_video(track)
    youtube.add_song_playlist(youtube_playlist_id, id)
    print("Added...")
    time.sleep(1)

print("Done 👍")
print(f"https://www.youtube.com/playlist?list={youtube_playlist_id}")