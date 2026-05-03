import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, SidebarComponent],
  template: `
    <!-- Layout Admin -->
    <div *ngIf="isStaffRoute()" class="admin-layout fade-in">
      <app-sidebar></app-sidebar>
      <main class="content-area">
        <router-outlet></router-outlet>
      </main>
    </div>

    <!-- Layout Client / Public -->
    <div *ngIf="!isStaffRoute()">
      <router-outlet></router-outlet>
    </div>
  `
})
export class AppComponent {
  constructor(public router: Router) {}

  isStaffRoute() {
    return ['/dashboard', '/calendrier', '/chambres', '/profil'].some(route => this.router.url.startsWith(route));
  }
}
