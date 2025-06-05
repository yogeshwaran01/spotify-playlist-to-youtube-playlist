from .spotify_client import SpotifyClient # Assuming relative import
from .youtube_client import YouTubeClient # Assuming relative import

class SyncManager:
    def __init__(self, spotify_client: SpotifyClient, youtube_client: YouTubeClient):
        if not spotify_client or not spotify_client.sp:
            raise ValueError("SpotifyClient is not properly initialized or authenticated.")
        if not youtube_client or not youtube_client.youtube:
             raise ValueError("YouTubeClient is not properly initialized or authenticated.")
        self.spotify_client = spotify_client
        self.youtube_client = youtube_client

    def convert_playlist(self, spotify_playlist_id: str, new_youtube_playlist_name: str) -> dict:
        tracks_added_count = 0
        errors = []

        # 1. Get tracks from Spotify playlist
        spotify_tracks, error = self.spotify_client.get_playlist_tracks(spotify_playlist_id)
        if error:
            return {"status": "error", "message": f"Failed to get Spotify playlist tracks: {error}", "details": None}
        if not spotify_tracks:
            return {"status": "error", "message": "No tracks found in the Spotify playlist or playlist is empty.", "details": None}

        # 2. Create a new YouTube playlist
        # For description, we can use something generic or include spotify_playlist_id
        youtube_playlist_description = f"Converted from Spotify playlist {spotify_playlist_id} by Tune2Tube."
        new_youtube_playlist_id = self.youtube_client.create_playlist(
            name=new_youtube_playlist_name,
            description=youtube_playlist_description,
            privacy_status="private" # Or allow user to choose
        )

        if not new_youtube_playlist_id:
            return {"status": "error", "message": "Failed to create YouTube playlist.", "details": None}

        # 3. For each Spotify track, search on YouTube and add to the new playlist
        for track_info in spotify_tracks:
            spotify_track_name = track_info.get('name')
            spotify_artist_name = track_info.get('artist')

            if not spotify_track_name or not spotify_artist_name:
                errors.append(f"Skipping track due to missing name or artist: {track_info}")
                continue

            query = f"{spotify_track_name} {spotify_artist_name}"
            youtube_video_id = self.youtube_client.search_track(query)

            if youtube_video_id:
                success = self.youtube_client.add_track_to_playlist(new_youtube_playlist_id, youtube_video_id)
                if success:
                    tracks_added_count += 1
                else:
                    errors.append(f"Failed to add '{query}' (Video ID: {youtube_video_id}) to YouTube playlist.")
            else:
                errors.append(f"No YouTube video found for '{query}'.")

        summary_message = f"Playlist '{new_youtube_playlist_name}' created on YouTube. Added {tracks_added_count} of {len(spotify_tracks)} tracks."
        if errors:
            summary_message += " Some tracks could not be added."
            return {
                "status": "partial_success",
                "message": summary_message,
                "youtube_playlist_id": new_youtube_playlist_id,
                "tracks_added": tracks_added_count,
                "total_spotify_tracks": len(spotify_tracks),
                "errors": errors
            }

        return {
            "status": "success",
            "message": summary_message,
            "youtube_playlist_id": new_youtube_playlist_id,
            "tracks_added": tracks_added_count,
            "total_spotify_tracks": len(spotify_tracks)
        }
