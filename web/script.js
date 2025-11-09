document.addEventListener('DOMContentLoaded', () => {
    const createBtn = document.getElementById('create-btn');
    const syncBtn = document.getElementById('sync-btn');

    createBtn.addEventListener('click', () => {
        const spotifyPlaylistId = document.getElementById('spotify-playlist-id-create').value;
        const playlistName = document.getElementById('youtube-playlist-name').value;
        const playlistDescription = document.getElementById('youtube-playlist-description').value;
        const privacy = document.querySelector('input[name="privacy"]:checked').value;

        if (!spotifyPlaylistId) {
            alert('Please enter a Spotify Playlist ID.');
            return;
        }

        const data = {
            spotify_playlist_id: spotifyPlaylistId,
            name: playlistName,
            description: playlistDescription,
            privacy: privacy,
        };

        fetch('/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Playlist created successfully! URL: ' + data.playlist_url);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please check the console for details.');
        });
    });

    syncBtn.addEventListener('click', () => {
        const spotifyPlaylistId = document.getElementById('spotify-playlist-id-sync').value;
        const youtubePlaylistId = document.getElementById('youtube-playlist-id-sync').value;

        if (!spotifyPlaylistId || !youtubePlaylistId) {
            alert('Please enter both Spotify and YouTube Playlist IDs.');
            return;
        }

        const data = {
            spotify_playlist_id: spotifyPlaylistId,
            youtube_playlist_id: youtubePlaylistId,
        };

        fetch('/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Playlists synced successfully!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please check the console for details.');
        });
    });
});
