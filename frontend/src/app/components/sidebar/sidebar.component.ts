import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ReservationService } from '../../services/reservation.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <aside class="sidebar h-100 shadow-luxury d-flex flex-column">
      <!-- Brand -->
      <div class="p-4 border-bottom border-white-10">
        <div class="d-flex align-items-center gap-3">
          <div class="brand-icon">
            <i class="bi bi-buildings-fill text-navy-deep"></i>
          </div>
          <div>
            <div class="font-display h5 mb-0 text-white">Maison Royale</div>
            <div class="text-gold small text-uppercase tracking-wider" style="font-size: 10px;">Admin Console</div>
          </div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-grow-1 px-3 py-4 overflow-auto">
        <a routerLink="/chambres" routerLinkActive="active" class="nav-link">
          <i class="bi bi-door-open"></i>
          <span>Chambres</span>
        </a>

        <div *ngIf="currentUser?.role === 'admin'">
          <div class="small text-white-50 text-uppercase tracking-widest mb-3 mt-4 ps-2" style="font-size: 10px;">Administration</div>
          
          <a routerLink="/dashboard" routerLinkActive="active" class="nav-link">
            <i class="bi bi-grid-1x2"></i>
            <span>Tableau de bord</span>
            <span *ngIf="hasNewNotification" class="badge bg-danger rounded-circle ms-2" style="width: 8px; height: 8px; padding: 0;"></span>
          </a>
          <a routerLink="/calendrier" routerLinkActive="active" class="nav-link">
            <i class="bi bi-calendar3"></i>
            <span>Calendrier</span>
          </a>
          <a routerLink="/admin/clients" routerLinkActive="active" class="nav-link">
            <i class="bi bi-people"></i>
            <span>Clients</span>
          </a>

          <div class="small text-white-50 text-uppercase tracking-widest mt-5 mb-3 ps-2" style="font-size: 10px;">Système</div>
          <a routerLink="/admin/settings" routerLinkActive="active" class="nav-link">
            <i class="bi bi-gear"></i>
            <span>Paramètres</span>
          </a>
        </div>
      </nav>

      <!-- User -->
      <div class="p-3 border-top border-white-10 mt-auto">
        <div class="d-flex align-items-center gap-3 p-2 rounded bg-white-5">
          <div class="user-avatar">{{ (currentUser?.nom || 'A')[0].toUpperCase() }}</div>
          <div class="flex-grow-1 min-w-0" (click)="clearNotifications()">
            <div class="small fw-bold text-white text-truncate">{{ currentUser?.nom || 'Admin' }}</div>
            <div class="text-white-50 smallest text-truncate">{{ currentUser?.role === 'admin' ? 'Administrateur' : 'Client' }}</div>
          </div>
          <button (click)="onLogout()" class="btn btn-link p-0 text-white-50 hover-gold" title="Déconnexion">
            <i class="bi bi-box-arrow-right fs-5"></i>
          </button>
        </div>
      </div>
    </aside>
  `,
  styles: [`
    .brand-icon { width: 40px; height: 40px; background: #c5a059; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
    .user-avatar { width: 36px; height: 36px; border-radius: 50%; background: #c5a059; color: #1a1e26; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
    .smallest { font-size: 11px; }
    .bg-white-5 { background: rgba(255,255,255,0.05); }
    .border-white-10 { border-color: rgba(255,255,255,0.1) !important; }
    .hover-gold:hover { color: #c5a059 !important; }
  `]
})
export class SidebarComponent implements OnInit {
  currentUser: any = null;
  hasNewNotification = false;

  constructor(
    private authService: AuthService, 
    private router: Router,
    private reservationService: ReservationService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => this.currentUser = user);
    this.reservationService.getUpdates().subscribe((update: any) => {
      if (update.type === 'create') {
        this.hasNewNotification = true;
      }
    });
  }

  clearNotifications() {
    this.hasNewNotification = false;
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
