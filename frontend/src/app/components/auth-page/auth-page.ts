import { Component } from '@angular/core';
import { AuthService } from '../../services/auth';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card'; // Import MatCardModule
import { MatIconModule, MatIconRegistry } from '@angular/material/icon'; // Import MatIconModule and MatIconRegistry
import { DomSanitizer } from '@angular/platform-browser'; // Import DomSanitizer
import { CommonModule } from '@angular/common'; // For *ngIf

// YouTube SVG Icon as a string
const YOUTUBE_ICON_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28.9 20.2" width="24" height="24">
  <path fill="#FF0000" d="M28.2 5.6s-.3-2.1-1.2-3C25.9 1.5 24.7 1.5 24.1 1.4 20.1.2 14.5.2 14.5.2s-5.6 0-9.6 1.3C4.2 1.5 3.1 1.5 1.9 2.6.9 3.6.7 5.6.7 5.6S.4 8 .4 10.4v1.5c0 2.4.3 4.7.3 4.7s.3 2.1 1.2 3c1.2 1.2 2.6 1.1 3.3 1.3 2.5.3 9 1.2 9.6 1.2s5.6 0 9.6-1.2c.7-.1 2.1-.1 3.3-1.3 1-1 1.2-3 1.2-3s.3-2.4.3-4.7v-1.5c0-2.4-.3-4.7-.3-4.7z"/>
  <path fill="#FFFFFF" d="M11.6 14.3V7.9l6.1 3.2z"/>
</svg>
`;

@Component({
  selector: 'app-auth-page',
  standalone: true,
  imports: [
    CommonModule, // For *ngIf
    MatButtonModule,
    MatCardModule,  // Add MatCardModule here
    MatIconModule   // Add MatIconModule here
  ],
  templateUrl: './auth-page.html',
  styleUrls: ['./auth-page.scss'] // Ensure this file exists or is created
})
export class AuthPageComponent {

  constructor(
    private authService: AuthService,
    private iconRegistry: MatIconRegistry,
    private sanitizer: DomSanitizer
  ) {
    this.iconRegistry.addSvgIconLiteral('youtube_logo', this.sanitizer.bypassSecurityTrustHtml(YOUTUBE_ICON_SVG));
  }

  onSpotifyLogin(): void {
    this.authService.loginWithSpotify();
  }

  onYouTubeLogin(): void {
    this.authService.loginWithYouTube();
  }
}
