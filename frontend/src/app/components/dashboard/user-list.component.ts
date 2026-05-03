import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container py-5">
      <div class="glass-card p-5 border-0 shadow-sm" style="border-radius: 30px;">
        <div class="d-flex justify-content-between align-items-center mb-5">
          <div>
            <h2 class="font-display h2 mb-1">Gestion des Clients</h2>
            <p class="text-muted small text-uppercase tracking-widest">Liste complète des membres de la Maison Royale</p>
          </div>
          <div class="badge bg-gold text-navy-deep px-3 py-2 rounded-pill shadow-sm">
            {{ users.length }} Utilisateurs inscrits
          </div>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="bg-light">
              <tr class="text-muted small text-uppercase tracking-wider">
                <th class="px-4 py-3 border-0">Membre</th>
                <th class="px-4 py-3 border-0">Email</th>
                <th class="px-4 py-3 border-0">Rôle</th>
                <th class="px-4 py-3 border-0">Date d'inscription</th>
                <th class="px-4 py-3 border-0 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let user of users">
                <td class="px-4 py-3">
                  <div class="d-flex align-items-center gap-3">
                    <div class="rounded-circle bg-navy text-gold d-flex align-items-center justify-content-center fw-bold" style="width: 40px; height: 40px;">
                      {{ (user.nom || 'U')[0].toUpperCase() }}
                    </div>
                    <span class="fw-bold">{{ user.nom || 'Anonyme' }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-muted">{{ user.email }}</td>
                <td class="px-4 py-3">
                  <span class="badge rounded-pill px-3" [ngClass]="user.role === 'admin' ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary'">
                    {{ user.role | titlecase }}
                  </span>
                </td>
                <td class="px-4 py-3 text-muted small">{{ user.createdAt | date:'dd/MM/yyyy' }}</td>
                <td class="px-4 py-3 text-end">
                  <button class="btn btn-sm btn-outline-dark rounded-circle me-2"><i class="bi bi-eye"></i></button>
                  <button class="btn btn-sm btn-outline-danger rounded-circle"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .font-display { font-family: 'Cormorant Garamond', serif; }
    .bg-navy { background-color: #1a1e26; }
    .text-gold { color: #c5a059; }
    .bg-gold { background-color: #c5a059; }
    .text-navy-deep { color: #1a1e26; }
  `]
})
export class UserListComponent implements OnInit {
  users: any[] = [];

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.getUsers().subscribe(data => {
      this.users = data;
    });
  }
}
