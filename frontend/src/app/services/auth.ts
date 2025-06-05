import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() { }

  loginWithSpotify(): void {
    // Assuming Flask backend runs on port 5000
    window.location.href = 'http://localhost:5000/auth/spotify/login';
  }

  loginWithYouTube(): void {
    // Assuming Flask backend runs on port 5000
    window.location.href = 'http://localhost:5000/auth/youtube/login';
  }
}
