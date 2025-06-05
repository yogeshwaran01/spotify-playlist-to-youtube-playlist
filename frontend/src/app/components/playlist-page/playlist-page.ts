import { Component, OnInit } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { PlaylistService, SpotifyPlaylist } from '../../services/playlist'; // Corrected path

import { FormsModule } from '@angular/forms'; // For ngModel
// Angular Material Modules
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common'; // For *ngIf, *ngFor, async pipe
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
// Import the conversion status component
import { ConversionStatusComponent } from '../conversion-status/conversion-status';


@Component({
  selector: 'app-playlist-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule, // For ngModel
    MatListModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    ConversionStatusComponent // Import here
  ],
  templateUrl: './playlist-page.html',
  styleUrls: ['./playlist-page.scss']
})
export class PlaylistPageComponent implements OnInit {
  playlists$: Observable<SpotifyPlaylist[]> = of([]);
  isLoading: boolean = true;
  error: string | null = null;

  // Conversion state properties
  selectedPlaylistId: string | null = null;
  newYouTubePlaylistName: string = '';
  isConverting: boolean = false;
  conversionResult: any = null;
  conversionError: string | null = null;

  constructor(private playlistService: PlaylistService) { }

  ngOnInit(): void {
    this.isLoading = true;
    this.error = null; // Clear error from previous loads
    this.conversionResult = null; // Clear previous conversion results
    this.conversionError = null;
    this.playlists$ = this.playlistService.getSpotifyPlaylists().pipe(
      tap(() => {
        this.isLoading = false;
      }),
      catchError(err => {
        this.isLoading = false;
        this.error = err.message || 'Failed to load playlists.';
        console.error("Error fetching playlists in component:", err);
        return of([]);
      })
    );
  }

  onPlaylistSelect(playlist: SpotifyPlaylist): void {
    this.selectedPlaylistId = playlist.id;
    this.newYouTubePlaylistName = playlist.name; // Pre-fill with Spotify playlist name
    this.conversionResult = null; // Clear previous results
    this.conversionError = null;  // Clear previous errors
    this.isConverting = false; // Reset conversion state
    console.log('Selected Spotify playlist for conversion:', playlist);
  }

  startConversion(): void {
    if (!this.selectedPlaylistId || !this.newYouTubePlaylistName.trim()) {
      this.conversionError = 'Please select a Spotify playlist and provide a name for the new YouTube playlist.';
      return;
    }

    this.isConverting = true;
    this.conversionResult = null;
    this.conversionError = null;

    this.playlistService.convertPlaylist(this.selectedPlaylistId, this.newYouTubePlaylistName.trim())
      .subscribe({
        next: (response) => {
          this.conversionResult = response;
          this.isConverting = false;
          console.log('Conversion successful:', response);
        },
        error: (err) => {
          // The error from PlaylistService should already be a user-friendly string
          this.conversionError = err.message || 'An unknown error occurred during conversion.';
          this.isConverting = false;
          console.error('Conversion error in component:', err);
        }
      });
  }
}
