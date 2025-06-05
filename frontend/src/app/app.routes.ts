import { Routes } from '@angular/router';
import { AuthPageComponent } from './components/auth-page/auth-page';
import { PlaylistPageComponent } from './components/playlist-page/playlist-page'; // Import PlaylistPageComponent

export const routes: Routes = [
    { path: 'login', component: AuthPageComponent },
    { path: 'playlists', component: PlaylistPageComponent }, // Added playlists route
    { path: '', redirectTo: '/login', pathMatch: 'full' }, // Default route
    // Add other routes here later, e.g.:
    // { path: 'status', component: ConversionStatusComponent },
    // { path: '**', redirectTo: '/login' } // Wildcard route for a 404 or redirect
];
