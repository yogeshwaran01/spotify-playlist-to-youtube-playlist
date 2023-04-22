# Spotify Playlist to YouTube Playlist

A simple python script to convert Spotify playlist into YouTube playlist

## Usage

1. Create Google clould project and enable YouTube Data API and download the credentials file and rename it to `client_secret.json`
2. Create spotify app and export `CLIENT_ID` and `CLIENT_SECRET` as environment variable

```bash
export CLIENT_ID="xxxxxxxxxxxxxxxxxx"
export CLIENT_SECRET="xxxxxxxxxxxxxxxx"
```

3. To get more info check [this](https://dev.to/yogeshwaran01/from-spotify-to-youtube-how-i-built-a-python-script-to-convert-playlists-2h89)

4. Install all requirements

```bash
pip install -r requirements.txt
```

5. Run the Script

```bash
python main.py <playlist_id>
```

## Contact Me

If you need more info or any support please feel free to contact [me](yogeshin247@gmail.com)
