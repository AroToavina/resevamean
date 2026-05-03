import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="min-vh-100 d-flex flex-wrap bg-white overflow-hidden">
      <!-- Visual side -->
      <div class="col-lg-6 d-none d-lg-block position-relative">
        <img
          src="assets/hotel-lobby.jpg"
          alt="Hall d'hôtel élégant"
          class="position-absolute top-0 start-0 w-100 h-100 object-fit-cover"
        />
        <div class="position-absolute top-0 start-0 w-100 h-100" style="background: linear-gradient(135deg, rgba(26, 30, 38, 0.9), rgba(45, 49, 58, 0.6));"></div>
        
        <div class="position-relative z-1 h-100 d-flex flex-column justify-content-between p-5 text-white">
          <div class="d-flex align-items-center gap-2">
            <div class="brand-icon-small">
              <i class="bi bi-buildings-fill text-navy-deep"></i>
            </div>
            <span class="font-display h3 mb-0 tracking-wide">Maison Royale</span>
          </div>
          <div style="max-width: 450px;">
            <h2 class="display-4 font-display leading-tight mb-4">
              L'art de recevoir, <span class="text-gold fst-italic">orchestré</span>.
            </h2>
            <p class="text-white-50 small leading-relaxed">
              Gérez vos réservations en temps réel, vos disponibilités et vos clients depuis une seule console raffinée.
            </p>
          </div>
        </div>
      </div>

      <!-- Form side -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center p-4 p-lg-5">
        <div class="w-100" style="max-width: 400px;">
          <div class="d-lg-none d-flex align-items-center gap-2 mb-5">
            <div class="brand-icon-small bg-navy">
              <i class="bi bi-buildings-fill text-gold"></i>
            </div>
            <span class="font-display h3 mb-0">Maison Royale</span>
          </div>

          <span class="text-gold smallest text-uppercase tracking-widest fw-bold">Espace privé</span>
          <h1 class="font-display h1 mt-3 mb-2">Bienvenue</h1>
          <p class="text-muted small mb-5">Connectez-vous pour accéder à votre séjour.</p>

          <form (ngSubmit)="onLogin()" #loginForm="ngForm" class="d-grid gap-4">
            <div class="space-y-2">
              <label class="smallest text-uppercase tracking-wider fw-bold text-muted mb-2 d-block">Email</label>
              <div class="input-group">
                <span class="input-group-text bg-light border-end-0 text-muted"><i class="bi bi-envelope"></i></span>
                <input
                  type="email"
                  name="email"
                  [(ngModel)]="email"
                  required
                  class="form-control border-start-0 bg-light"
                  placeholder="votre@email.com"
                />
              </div>
            </div>

            <div class="space-y-2">
              <label class="smallest text-uppercase tracking-wider fw-bold text-muted mb-2 d-block">Mot de passe</label>
              <div class="input-group">
                <span class="input-group-text bg-light border-end-0 text-muted"><i class="bi bi-lock"></i></span>
                <input
                  type="password"
                  name="password"
                  [(ngModel)]="password"
                  required
                  class="form-control border-start-0 bg-light"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              [disabled]="loading"
              class="btn btn-navy-deep text-white w-100 py-3 mt-3 d-flex align-items-center justify-content-center gap-2 shadow"
            >
              {{ loading ? 'Connexion...' : 'Se connecter' }}
              <i class="bi bi-arrow-right" *ngIf="!loading"></i>
            </button>

            <p class="text-center small text-muted mt-4">
              Nouveau client ?
              <a routerLink="/register" class="text-navy-deep fw-bold text-decoration-none hover-gold ms-1">
                Créer un compte
              </a>
            </p>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .brand-icon-small { width: 36px; height: 36px; background: #c5a059; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
    .btn-navy-deep { background-color: #1a1e26; border-color: #1a1e26; transition: all 0.3s; }
    .btn-navy-deep:hover { background-color: #000; transform: translateY(-2px); }
    .hover-gold:hover { color: #c5a059 !important; }
    .font-display { font-family: 'Cormorant Garamond', serif; }
    .smallest { font-size: 10px; }
  `]
})
export class LoginComponent implements OnInit {
  email = '';
  password = '';
  loading = false;
  returnUrl: string = '/';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
  }

  onLogin() {
    this.loading = true;
    this.authService.login({ email: this.email, password: this.password }).subscribe({
      next: (res) => {
        if (res.user) {
          localStorage.setItem('user', JSON.stringify(res.user));
          if (res.user.role === 'admin') {
            this.router.navigate(['/dashboard']);
          } else {
            this.router.navigate(['/accueil-client']);
          }
        }
      },
      error: () => {
        alert('Identifiants incorrects.');
        this.loading = false;
      }
    });
  }
}
