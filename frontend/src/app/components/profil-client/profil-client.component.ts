import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReservationService } from '../../services/reservation.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-profil-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-vh-100 bg-light py-5">
      <div class="container">
        <div class="row g-4">
          <!-- Sidebar Profil & Edition -->
          <div class="col-lg-4">
            <div class="glass-card p-5 border-0 shadow-sm mb-4" style="border-radius: 30px;">
              <div class="text-center mb-4">
                <div class="rounded-circle bg-gold text-white d-inline-flex align-items-center justify-content-center shadow-lg mb-3" 
                     style="width: 100px; height: 100px; font-size: 40px; font-family: 'Cormorant Garamond', serif;">
                  {{ (currentUser?.nom || 'U')[0].toUpperCase() }}
                </div>
                <h3 class="font-display fw-bold mb-1">{{ currentUser?.nom || 'Client Royale' }}</h3>
                <p class="text-gold smallest text-uppercase tracking-widest">Membre de la Maison</p>
              </div>

              <form (ngSubmit)="onUpdateProfile()">
                <div class="mb-3">
                  <label class="form-label smallest fw-bold text-uppercase tracking-wider">Nom complet</label>
                  <input type="text" name="nom" [(ngModel)]="editModel.nom" class="form-control border-0 bg-light" style="border-radius: 10px;">
                </div>
                <div class="mb-4">
                  <label class="form-label smallest fw-bold text-uppercase tracking-wider">Email</label>
                  <input type="email" name="email" [(ngModel)]="editModel.email" class="form-control border-0 bg-light" style="border-radius: 10px;">
                </div>
                <button type="submit" [disabled]="loading" class="btn btn-navy w-100 py-2 rounded-pill shadow-sm">
                  {{ loading ? 'Mise à jour...' : 'Sauvegarder les modifications' }}
                </button>
              </form>
            </div>
          </div>

          <!-- Historique des Réservations -->
          <div class="col-lg-8">
            <div class="glass-card p-4 p-md-5 border-0 shadow-sm" style="border-radius: 30px;">
              <div class="d-flex justify-content-between align-items-center mb-5">
                <h2 class="font-display h3 mb-0">Mes Réservations</h2>
                <span class="badge bg-navy px-3 py-2 rounded-pill">{{ myReservations.length }} Séjours</span>
              </div>

              <div *ngIf="myReservations.length === 0" class="text-center py-5">
                <i class="bi bi-calendar-x display-1 text-light mb-3"></i>
                <p class="text-muted">Vous n'avez pas encore de réservations.</p>
              </div>

              <div class="space-y-4">
                <div *ngFor="let res of myReservations" class="p-4 rounded-4 bg-white border border-light shadow-sm mb-4">
                  <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
                    <div class="d-flex align-items-center gap-4">
                      <div class="bg-light p-3 rounded-3 text-center" style="min-width: 70px;">
                        <div class="fw-bold h4 mb-0 text-navy">{{ res.dateArrivee | date:'dd' }}</div>
                        <div class="smallest text-uppercase text-muted">{{ res.dateArrivee | date:'MMM' }}</div>
                      </div>
                      <div>
                        <h5 class="mb-1 fw-bold">{{ res.chambreId?.type || 'Chambre Deluxe' }}</h5>
                        <p class="text-muted small mb-0">Chambre n°{{ res.chambreId?.numero }} — {{ res.montantTotal }} MRU</p>
                      </div>
                    </div>
                    <div class="text-end">
                      <span class="badge-luxury" [ngClass]="res.statut">
                        {{ res.statut | titlecase }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .font-display { font-family: 'Cormorant Garamond', serif; }
    .bg-gold { background-color: #c5a059; }
    .text-gold { color: #c5a059; }
    .btn-navy { background-color: #1a1e26; color: white; transition: all 0.3s; }
    .badge-luxury { display: inline-block; padding: 6px 16px; border-radius: 100px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .badge-luxury.confirmee { background: #e8f5e9; color: #2e7d32; }
    .badge-luxury.en_attente { background: #fff8e1; color: #f57f17; }
    .smallest { font-size: 11px; }
  `]
})
export class ProfilClientComponent implements OnInit {
  currentUser: any = null;
  myReservations: any[] = [];
  editModel = { nom: '', email: '' };
  loading = false;

  constructor(
    private reservationService: ReservationService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user) {
        this.editModel = { nom: user.nom, email: user.email };
        this.loadMyReservations(user.nom || user.email);
      }
    });
  }

  loadMyReservations(clientName: string) {
    this.reservationService.getReservations().subscribe(data => {
      this.myReservations = data.filter(r => r.clientId === clientName);
    });
  }

  onUpdateProfile() {
    if (!this.currentUser) return;
    this.loading = true;
    this.authService.updateUser(this.currentUser.id || this.currentUser._id, this.editModel).subscribe({
      next: () => {
        alert('Profil mis à jour avec succès !');
        this.loading = false;
      },
      error: (err) => {
        alert('Erreur lors de la mise à jour : ' + (err.error?.message || 'Erreur technique'));
        this.loading = false;
      }
    });
  }
}
