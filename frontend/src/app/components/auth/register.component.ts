import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light p-4">
      <div class="glass-card p-5 shadow-lg border-0 bg-white" style="max-width: 500px; width: 100%; border-radius: 30px;">
        <div class="text-center mb-5">
          <h2 class="font-display display-5 mb-2">Rejoindre l'Excellence</h2>
          <p class="text-muted small text-uppercase tracking-widest">Créer votre compte Maison Royale</p>
        </div>

        <form (ngSubmit)="onRegister()" #registerForm="ngForm" class="d-grid gap-4">
          <div>
            <label class="form-label smallest fw-bold text-uppercase tracking-wider text-muted mb-2">Nom Complet</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-0"><i class="bi bi-person"></i></span>
              <input type="text" name="nom" [(ngModel)]="model.nom" required class="form-control border-0 bg-light py-3" placeholder="Ex: Ahmed Fall">
            </div>
          </div>

          <div>
            <label class="form-label smallest fw-bold text-uppercase tracking-wider text-muted mb-2">Email</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-0"><i class="bi bi-envelope"></i></span>
              <input type="email" name="email" [(ngModel)]="model.email" required class="form-control border-0 bg-light py-3" placeholder="votre@email.com">
            </div>
          </div>

          <div>
            <label class="form-label smallest fw-bold text-uppercase tracking-wider text-muted mb-2">Mot de passe</label>
            <div class="input-group">
              <span class="input-group-text bg-light border-0"><i class="bi bi-lock"></i></span>
              <input type="password" name="password" [(ngModel)]="model.password" required class="form-control border-0 bg-light py-3" placeholder="••••••••">
            </div>
          </div>

          <button type="submit" [disabled]="!registerForm.valid || loading" class="btn btn-navy w-100 py-3 rounded-pill shadow mt-2">
            {{ loading ? 'Création en cours...' : 'Créer mon compte' }}
          </button>

          <p class="text-center small text-muted mt-3">
            Déjà client ? 
            <a routerLink="/login" class="text-gold fw-bold text-decoration-none ms-1">Se connecter</a>
          </p>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .font-display { font-family: 'Cormorant Garamond', serif; font-weight: 700; }
    .btn-navy { background-color: #1a1e26; color: white; transition: all 0.3s; }
    .btn-navy:hover { background-color: #000; transform: translateY(-2px); }
    .text-gold { color: #c5a059; }
    .smallest { font-size: 11px; }
  `]
})
export class RegisterComponent {
  model = { nom: '', email: '', password: '', role: 'client' };
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  onRegister() {
    this.loading = true;
    this.authService.register(this.model).subscribe({
      next: () => {
        // Connexion automatique après inscription
        this.authService.login({ email: this.model.email, password: this.model.password }).subscribe({
          next: () => {
            alert('Compte créé et connecté avec succès !');
            this.router.navigate(['/accueil-client']);
          },
          error: () => {
            alert('Compte créé, veuillez vous connecter.');
            this.router.navigate(['/login']);
          }
        });
      },
      error: (err) => {
        alert('Erreur lors de la création : ' + (err.error?.message || 'Email déjà utilisé'));
        this.loading = false;
      }
    });
  }
}
