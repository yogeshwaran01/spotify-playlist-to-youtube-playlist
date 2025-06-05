import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon'; // For potential icons in messages

@Component({
  selector: 'app-conversion-status',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './conversion-status.html',
  styleUrls: ['./conversion-status.scss']
})
export class ConversionStatusComponent {
  @Input() result: any = null;
  @Input() error: string | null = null;

  constructor() { }
}
