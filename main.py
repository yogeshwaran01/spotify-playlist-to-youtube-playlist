import datetime
import json
import time

import click

from spotify_client import SpotifyClient
from sync_manager import SyncManager
from youtube_client import YouTubeClient

manager = SyncManager()


@click.group()
def cli():
    """
    Tune2Tube \n
    From Spotify's Groove to YouTube's Show: Seamless Conversion! \n
    GitHub: https://github.com/yogeshwaran01/spotify-playlist-to-youtube-playlist
    """


@click.command()
@click.argument("spotify_playlist_id")
@click.option("--public", is_flag=True, help="Create a public playlist")
@click.option("--private", is_flag=True, help="Create a public playlist")
@click.option("--name", "-n", help="Name of the YouTube playlist to be created")
@click.option("--description", "-d", help="Description of the playlist")
@click.option(
    "--only-link",
    "-l",
    default=False,
    help="just only link of playlist, logs not appear",
    is_flag=True,
)
@click.option(
    "--save-to-sync", "-s", is_flag=True, help="Save to list of playlist to sync"
)
def create(
    spotify_playlist_id: str,
    public: bool,
    private: bool,
    name: str,
    description: str,
    only_link: bool,
    save_to_sync: bool,
):
    """Create a YouTube Playlist from Spotify Playlist"""

    spotify = SpotifyClient()
    youtube = YouTubeClient()

# Get Songlist from Spotify
    
    spotify_playlist = spotify.get_playlist(spotify_playlist_id)

    if public:
        privacy_status = "public"
    elif private:
        privacy_status = "private"
    else:
        privacy_status = "private"

# Generate YouTube Playlist
    
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

    # SearchSongonYouTUbe
    
    for track in spotify_playlist.tracks:
        if not only_link:
            click.secho(f"Searching for {track}", fg="blue")
        video = youtube.search_video(track)
        if not only_link:
            click.secho(f"Song found: {video.title}", fg="green")
        youtube.add_song_playlist(youtube_playlist_id, video.video_id)
        if not only_link:
            click.secho("Song added", fg="green")
        time.sleep(1)

    if not only_link:
        click.secho(f"Playlist {privacy_status} playlist created", fg="blue")
        click.secho(
            f"Playlist found at https://www.youtube.com/playlist?list={youtube_playlist_id}", fg="blue"
        )
        click.secho(f"Playlist ID: {youtube_playlist_id}", fg="blue")
    else:
        click.secho(f"https://www.youtube.com/playlist?list={youtube_playlist_id}", fg="blue")

    if save_to_sync:
        manager.add_playlist(spotify_playlist_id, youtube_playlist_id, spotify_playlist.name, name, f"https://open.spotify.com/playlist/{spotify_playlist_id}", f"https://www.youtube.com/playlist?list={youtube_playlist_id}")
        manager.commit()


@click.command()
@click.option("-s", "--spotify_playlist_id", help="Spotify playlist ID")
@click.option("-y", "--youtube_playlist_id", help="YouTube playlist ID")
@click.option(
    "--only-link",
    "-l",
    default=False,
    help="just only link of playlist, logs not appear",
    is_flag=True,
)
def sync(
    spotify_playlist_id: str,
    youtube_playlist_id: str,
    only_link: bool,
):
    """Sync your YouTube playlist with Spotify Playlist"""

    playlists_to_be_synced = []

    if spotify_playlist_id is None and youtube_playlist_id is None:
        click.secho("Syncing Playlists ..", fg="blue")
        playlists_to_be_synced = manager.playlists_to_be_synced

    else:
        playlists_to_be_synced.append(
            {
                "spotify_playlist_id": spotify_playlist_id,
                "youtube_playlist_id": youtube_playlist_id,
            }
        )

    spotify = SpotifyClient()
    youtube = YouTubeClient()

# Sync between Spotify to YouTUbe
    
    for playlist in playlists_to_be_synced:
        if not only_link:
            click.secho(
                f"Syncing between Spotify: {playlist['spotify_playlist_id']} and YouTube: {playlist['youtube_playlist_id']}", fg="blue"
            )

        spotify_playlist = spotify.get_playlist(playlist["spotify_playlist_id"])
        youtube_playlist = youtube.get_playlist(playlist["youtube_playlist_id"])
        youtube_playlist_ids = list(
            map(
                lambda x: {
                    "id": x["snippet"]["resourceId"]["videoId"],
                    "item": x["id"],
                },
                youtube_playlist,
            )
        )
        yt_p_ids = list(
            map(lambda x: x["snippet"]["resourceId"]["videoId"], youtube_playlist)
        )

        searched_playlist = []
        for track in spotify_playlist.tracks:
            video = youtube.search_video(track)
            searched_playlist.append(video.video_id)

        songs_to_be_added = []
        songs_to_be_removed = []

        for song in youtube_playlist_ids:
            if song["id"] not in searched_playlist:
                songs_to_be_removed.append(song["item"])

        for song in searched_playlist:
            if song not in yt_p_ids:
                songs_to_be_added.append(song)

        if not only_link:
            click.secho("Adding songs ...", fg="green")
        with click.progressbar(songs_to_be_added) as bar:
            for song in bar:
                youtube.add_song_playlist(playlist["youtube_playlist_id"], song)

        if not only_link:
            click.secho("Removing songs ...", fg="green")
        with click.progressbar(songs_to_be_removed) as bar:
            for song in bar:
                youtube.remove_song_playlist(playlist["youtube_playlist_id"], song)

        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not only_link:
            click.secho(f"Spotify playlist {spotify_playlist.name} Synced on {t}", fg="blue")
            click.secho(
                f"Playlist found at https://www.youtube.com/playlist?list={playlist['youtube_playlist_id']}", fg="blue"
            )
        else:
            click.secho(
                f"https://www.youtube.com/playlist?list={playlist['youtube_playlist_id']}", fg="blue"
            )

# Clear playlists

@click.command()
def clear():
    """Clear all the playlists thats to be synced"""
    with open(manager.playlist_file, "w") as file:
        json.dump([], file)

    click.secho("cleared", fg="blue")


cli.add_command(create)
cli.add_command(sync)
cli.add_command(clear)

if __name__ == "__main__":
    cli()
