import click
import logging
import time
import datetime

from spotify_client import SpotifyClient
from youtube_client import YouTubeClient

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    """
    Tune2Tube \n
    From Spotify's Groove to YouTube's Show: Seamless Conversion! \n
    GitHub: https://github.com/yogeshwaran01/spotify-playlist-to-youtube-playlist
    """


@click.command()
@click.argument("spotify_playlist_id")
@click.option("--public", is_flag=True, help="create a public playlist")
@click.option("--name", "-n", help="Name of the YouTube playlist to be created")
@click.option("--description", "-d", help="Description of the playlist")
def create(spotify_playlist_id: str, public: bool, name: str, description: str):
    """Create a YouTube Playlist from Spotify Playlist"""

    spotify = SpotifyClient()
    youtube = YouTubeClient()

    spotify_playlist = spotify.get_playlist(spotify_playlist_id)

    if public:
        privacy_status = "public"
    else:
        privacy_status = "private"
    
    if name and description:
        youtube_playlist_id = youtube.create_playlist(
            name,
            description,
            privacy_status=privacy_status,
        )["id"]
    elif description:
        youtube_playlist_id = youtube.create_playlist(
            spotify_playlist.name,
            description,
            privacy_status=privacy_status,
        )["id"]
    elif name:
        youtube_playlist_id = youtube.create_playlist(
            name,
            spotify_playlist.description,
            privacy_status=privacy_status,
        )["id"]
    else:
        youtube_playlist_id = youtube.create_playlist(
            spotify_playlist.name,
            spotify_playlist.description,
            privacy_status=privacy_status,
        )["id"]

    for track in spotify_playlist.tracks:
        logging.info(f"Searching for {track}")
        video = youtube.search_video(track)
        logging.info(f"Song found: {video.title}")
        youtube.add_song_playlist(youtube_playlist_id, video.video_id)
        logging.info("Song added")
        time.sleep(1)

    logging.info(f"Playlit {privacy_status} playlist created")
    logging.info(
        f"Playlist found at https://www.youtube.com/playlist?list={youtube_playlist_id}"
    )
    logging.info(f"Playlist ID: {youtube_playlist_id}")


@click.command()
@click.argument("spotify_playlist_id")
@click.argument("youtube_playlist_id")
def sync(spotify_playlist_id: str, youtube_playlist_id: str):
    """Sync your YouTube playlist with Spotify Playlist"""
    spotify = SpotifyClient()
    youtube = YouTubeClient()

    logging.info("Syncing ...")

    spotify_playlist = spotify.get_playlist(spotify_playlist_id)
    youtube_playlist = youtube.get_playlist(youtube_playlist_id)
    youtube_playlist_ids = list(
        map(
            lambda x: {"id": x["snippet"]["resourceId"]["videoId"], "item": x["id"]},
            youtube_playlist,
        )
    )
    yt_p_ids = list(
        map(lambda x: x["snippet"]["resourceId"]["videoId"], youtube_playlist)
    )
    # print(youtube_playlist_ids)

    searched_playlist = []
    for track in spotify_playlist.tracks:
        video = youtube.search_video(track)
        searched_playlist.append(video.video_id)

    # print(searched_playlist)

    songs_to_be_added = []
    songs_to_be_removed = []

    for song in youtube_playlist_ids:
        if song["id"] not in searched_playlist:
            songs_to_be_removed.append(song["item"])

    for song in searched_playlist:
        if song not in yt_p_ids:
            songs_to_be_added.append(song)

    for song in songs_to_be_added:
        youtube.add_song_playlist(youtube_playlist_id, song)

    for song in songs_to_be_removed:
        youtube.remove_song_playlist(youtube_playlist_id, song)

    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logging.info(f"Spotify playlist {spotify_playlist.name} Synced on {t}")
    logging.info(
        f"Playlist found at https://www.youtube.com/playlist?list={youtube_playlist_id}"
    )


cli.add_command(create)
cli.add_command(sync)

if __name__ == "__main__":
    cli()
