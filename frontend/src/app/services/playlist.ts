import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

export interface SpotifyPlaylist {
  id: string;
  name: string;
  owner: string;
  tracks_total: number;
}

@Injectable({
  providedIn: 'root'
})
export class PlaylistService {
  private spotifyPlaylistsUrl = 'http://localhost:5000/api/spotify/playlists';

  constructor(private http: HttpClient) { }

  getSpotifyPlaylists(): Observable<SpotifyPlaylist[]> {
    return this.http.get<SpotifyPlaylist[]>(this.spotifyPlaylistsUrl).pipe(
      tap(playlists => console.log('Fetched Spotify playlists:', playlists)),
      catchError(err => this.handleError(err, 'getSpotifyPlaylists'))
    );
  }

  convertPlaylist(spotifyPlaylistId: string, youtubePlaylistName: string): Observable<any> {
    const convertUrl = 'http://localhost:5000/api/convert';
    const body = {
      spotify_playlist_id: spotifyPlaylistId,
      youtube_playlist_name: youtubePlaylistName
    };
    return this.http.post<any>(convertUrl, body).pipe(
      tap(response => console.log('Conversion API response:', response)),
      catchError(err => this.handleError(err, 'convertPlaylist'))
    );
  }

  private handleError(error: HttpErrorResponse, methodName: string = 'operation'): Observable<never> {
    let userMessage = 'An unknown error occurred!';

    if (error.error instanceof ErrorEvent) {
      // Client-side or network error
      userMessage = `A client-side or network error occurred: ${error.error.message}`;
    } else {
      // Backend returned an unsuccessful response code
      // The error object might contain a user-friendly message from the server
      if (error.error && error.error.error) {
        userMessage = `Error: ${error.error.error}`;
        if (error.error.details) {
          userMessage += ` Details: ${error.error.details}`;
        }
      } else {
        userMessage = `Server returned code ${error.status}. Please try again later.`;
      }

      if (error.status === 401) {
        if (methodName === 'convertPlaylist') {
            userMessage = 'Unauthorized: Your session may have expired or you lack permissions. Please ensure you are logged in with both Spotify and YouTube, then try again.';
        } else {
            userMessage = 'Unauthorized: Please log in again.';
        }
      } else if (error.status === 400) {
        // Specific handling for bad requests if backend provides detailed errors
        if (error.error && error.error.error) {
             userMessage = `Bad Request: ${error.error.error}`;
        } else {
            userMessage = 'Bad Request: Please check your input and try again.';
        }
      }
    }
    console.error(`PlaylistService (${methodName}): ${userMessage}`, error);
    // Return an error that the component can display
    return throwError(() => new Error(userMessage));
  }
}
