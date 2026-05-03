import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReservationService } from '../../services/reservation.service';
import { ChambreService } from '../../services/chambre.service';
import { PaiementService } from '../../services/paiement.service';

@Component({
  selector: 'app-reservation-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="glass-card p-4 border-0 h-100">
      <div class="mb-4">
        <h5 class="fw-bold m-0" style="font-family: 'Cormorant Garamond', serif;">{{ createdReservation ? 'Paiement Bankily' : 'Nouvelle Réservation' }}</h5>
        <p class="text-muted small">{{ createdReservation ? 'Finalisez votre réservation' : 'Saisissez les détails du séjour' }}</p>
      </div>
      
      <form *ngIf="!createdReservation" (ngSubmit)="onSubmit()" #resForm="ngForm">
        <div class="mb-3">
          <label class="form-label small fw-bold text-uppercase">Client</label>
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-person"></i></span>
            <input type="text" class="form-control border-start-0 ps-0" [(ngModel)]="model.clientId" name="clientId" placeholder="Nom ou Email" required>
          </div>
        </div>
        
        <div class="row g-3 mb-3">
          <div class="col-6">
            <label class="form-label small fw-bold text-uppercase">Arrivée</label>
            <input type="date" class="form-control" [(ngModel)]="model.dateArrivee" name="dateArrivee" required>
          </div>
          <div class="col-6">
            <label class="form-label small fw-bold text-uppercase">Départ</label>
            <input type="date" class="form-control" [(ngModel)]="model.dateDepart" name="dateDepart" required>
          </div>
        </div>
        
        <div class="mb-4">
          <label class="form-label small fw-bold text-uppercase">Chambre</label>
          <select class="form-select" [(ngModel)]="model.chambreId" name="chambreId" required>
            <option value="" disabled selected>Choisir une chambre...</option>
            <option *ngFor="let c of chambres" [value]="c._id">
              Chambre {{ c.numero }} — {{ c.type }} ({{ c.prixParNuit }} MRU)
            </option>
          </select>
        </div>
        
        <button type="submit" [disabled]="!resForm.form.valid" class="btn btn-accent w-100 py-3 mt-2 shadow">
          <i class="bi bi-check2-circle me-2"></i> Valider la Réservation
        </button>
      </form>

      <div *ngIf="createdReservation" class="text-center animate-fade-in">
        <div class="alert alert-success small py-2 mb-4">Réservation n°{{ createdReservation._id.substring(18) }} enregistrée</div>
        
        <div class="mb-4">
          <label class="form-label small fw-bold text-uppercase d-block mb-3">Numéro Bankily</label>
          <div class="input-group mb-3">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-phone"></i></span>
            <input type="text" class="form-control border-start-0 ps-0" [(ngModel)]="bankilyPhone" placeholder="Ex: 44123456" required>
          </div>
          <p class="small text-muted mb-4">Montant à régler : <strong>{{ createdReservation.montantTotal || 0 }} MRU</strong></p>
        </div>

        <button (click)="onPay()" [disabled]="!bankilyPhone || isPaying" class="btn btn-success w-100 py-3 shadow mb-3">
          <span *ngIf="!isPaying"><i class="bi bi-wallet2 me-2"></i> Payer via Bankily</span>
          <span *ngIf="isPaying" class="spinner-border spinner-border-sm me-2"></span>
        </button>

        <button (click)="createdReservation = null" class="btn btn-link btn-sm text-decoration-none text-muted">Annuler et revenir</button>
      </div>
    </div>
  `
})
export class ReservationFormComponent implements OnInit {
  model = {
    clientId: '',
    dateArrivee: '',
    dateDepart: '',
    chambreId: '',
    statut: 'en_attente'
  };

  chambres: any[] = [];
  createdReservation: any = null;
  bankilyPhone: string = '';
  isPaying: boolean = false;

  constructor(
    private reservationService: ReservationService,
    private chambreService: ChambreService,
    private paiementService: PaiementService
  ) {}

  ngOnInit(): void {
    this.chambreService.getChambres().subscribe(data => this.chambres = data);
  }

  onSubmit() {
    this.reservationService.createReservation(this.model).subscribe({
      next: (res) => {
        this.createdReservation = res;
      },
      error: (err) => alert('Erreur : ' + (err.error?.message || 'Une erreur est survenue'))
    });
  }

  onPay() {
    this.isPaying = true;
    this.paiementService.payerBankily(
      this.createdReservation._id, 
      this.createdReservation.montantTotal || 1000, 
      this.bankilyPhone
    ).subscribe({
      next: () => {
        alert('Paiement réussi ! Votre réservation est confirmée.');
        this.isPaying = false;
        this.createdReservation = null;
        this.model = { clientId: '', dateArrivee: '', dateDepart: '', chambreId: '', statut: 'en_attente' };
      },
      error: (err) => {
        alert('Échec du paiement : ' + (err.error?.message || 'Erreur inconnue'));
        this.isPaying = false;
      }
    });
  }
}
