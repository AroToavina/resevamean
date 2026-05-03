import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container py-5">
      <h2 class="font-display h2 mb-4">Paramètres de l'Hôtel</h2>
      <div class="glass-card p-5 border-0 shadow-sm" style="border-radius: 30px;">
        <div class="row g-4">
          <div class="col-md-6">
            <label class="form-label text-muted small fw-bold text-uppercase">Nom de l'établissement</label>
            <input type="text" [(ngModel)]="settings.nom" class="form-control form-control-lg border-0 bg-light">
          </div>
          <div class="col-md-6">
            <label class="form-label text-muted small fw-bold text-uppercase">Email de contact</label>
            <input type="email" [(ngModel)]="settings.email" class="form-control form-control-lg border-0 bg-light">
          </div>
        </div>
        <button class="btn btn-navy mt-4 px-5 rounded-pill" (click)="save()">Enregistrer</button>
      </div>
    </div>
  `
})
export class SettingsComponent {
  settings = { nom: 'Maison Royale', email: 'contact@maisonroyale.com' };
  save() { alert('Paramètres sauvegardés !'); }
}
