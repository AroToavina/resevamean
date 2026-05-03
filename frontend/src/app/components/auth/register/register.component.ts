import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
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
              Rejoignez <span class="text-gold fst-italic">l'excellence</span>.
            </h2>
            <p class="text-white-50 small leading-relaxed">
              Créez votre compte pour gérer vos réservations et profiter d'un service hôtelier sur mesure.
            </p>
          </div>
        </div>
      </div>

      <!-- Form side -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center p-4 p-lg-5">
        <div class="w-100" style="max-width: 400px;">
          <span class="text-gold smallest text-uppercase tracking-widest fw-bold">Nouveau client</span>
          <h1 class="font-display h1 mt-3 mb-2">Créer un compte</h1>
          <p class="text-muted small mb-5">Inscrivez-vous pour commencer votre expérience.</p>

          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="d-grid gap-3">
            <div class="space-y-1">
              <label class="smallest text-uppercase tracking-wider fw-bold text-muted mb-1 d-block">Nom complet</label>
              <input type="text" formControlName="nom" class="form-control bg-light" placeholder="Ex: Jean Dupont">
            </div>

            <div class="space-y-1">
              <label class="smallest text-uppercase tracking-wider fw-bold text-muted mb-1 d-block">Email</label>
              <input type="email" formControlName="email" class="form-control bg-light" placeholder="jean@email.com">
            </div>

            <div class="space-y-1">
              <label class="smallest text-uppercase tracking-wider fw-bold text-muted mb-1 d-block">Mot de passe</label>
              <input type="password" formControlName="password" class="form-control bg-light" placeholder="••••••••">
            </div>

            <button type="submit" [disabled]="registerForm.invalid" class="btn btn-navy-deep text-white w-100 py-3 mt-3 shadow">
              S'inscrire
            </button>

            <p class="text-center small text-muted mt-4">
              Déjà un compte ?
              <a routerLink="/login" class="text-navy-deep fw-bold text-decoration-none hover-gold ms-1">
                Se connecter
              </a>
            </p>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .brand-icon-small {
      width: 36px;
      height: 36px;
      background: var(--gold);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
    }
    .btn-navy-deep {
      background-color: var(--navy-deep);
      border-color: var(--navy-deep);
    }
    .hover-gold:hover { color: var(--gold) !important; }
    .object-fit-cover { object-fit: cover; }
    .smallest { font-size: 10px; }
  `]
})
export class RegisterComponent {
  registerForm: FormGroup;

  constructor(
    private fb: FormBuilder, 
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      nom: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.authService.register(this.registerForm.value).subscribe({
        next: () => {
          alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
          this.router.navigate(['/login']);
        },
        error: (err) => alert('Erreur lors de l\'inscription: ' + (err.error?.message || err.message))
      });
    }
  }
}
