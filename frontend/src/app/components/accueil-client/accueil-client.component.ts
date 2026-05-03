import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChambreService } from '../../services/chambre.service';
import { ReservationService } from '../../services/reservation.service';
import { PaiementService } from '../../services/paiement.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-accueil-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="min-vh-100 bg-light">
      <div class="bg-navy py-5 text-center text-white mb-5 shadow-sm" style="background: linear-gradient(135deg, #1a1e26 0%, #2c3441 100%);">
        <h1 class="font-display display-4 mb-2">Maison Royale</h1>
        <p class="text-gold smallest text-uppercase tracking-widest">Réservation de prestige en temps réel</p>
      </div>

      <div class="container pb-5">
        <!-- Liste des chambres -->
        <div class="row g-4" *ngIf="!chambreSelectionnee && !reservationCreee">
          <div class="col-lg-4 col-md-6" *ngFor="let chambre of chambres">
            <div class="card h-100 border-0 shadow-sm overflow-hidden card-hover" style="border-radius: 20px;">
              <div class="position-relative">
                <img [src]="chambre.image" class="card-img-top" [alt]="chambre.type" style="height: 250px; object-fit: cover;">
                <div class="position-absolute top-0 end-0 m-3">
                  <span class="badge bg-gold text-navy px-3 py-2 rounded-pill shadow-sm">{{ chambre.prixParNuit }} MRU / nuit</span>
                </div>
              </div>
              <div class="card-body p-4">
                <h5 class="fw-bold mb-2 font-display" style="font-size: 1.5rem;">{{ chambre.type }}</h5>
                <p class="text-muted small mb-4">{{ chambre.description }}</p>
                <button class="btn btn-navy w-100 py-3 rounded-pill shadow-sm" (click)="selectionnerChambre(chambre)">
                  Choisir cette suite <i class="bi bi-arrow-right ms-2"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Formulaire de Dates -->
        <div *ngIf="chambreSelectionnee && !reservationCreee" class="row justify-content-center animate-fade-in">
          <div class="col-lg-7">
            <div class="glass-card p-5 border-0 shadow-lg" style="border-radius: 30px;">
              <div class="d-flex align-items-center mb-4">
                <button class="btn btn-link text-navy p-0 me-3" (click)="chambreSelectionnee = null">
                  <i class="bi bi-chevron-left fs-4"></i>
                </button>
                <h2 class="font-display mb-0">Détails du Séjour</h2>
              </div>

              <div class="row g-3 mb-5">
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-uppercase tracking-wider">Arrivée</label>
                  <input type="date" class="form-control form-control-lg border-0 shadow-sm" [(ngModel)]="reservation.dateArrivee" (change)="calculerTotal()">
                </div>
                <div class="col-md-6">
                  <label class="form-label small fw-bold text-uppercase tracking-wider">Départ</label>
                  <input type="date" class="form-control form-control-lg border-0 shadow-sm" [(ngModel)]="reservation.dateDepart" (change)="calculerTotal()">
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center p-4 bg-light rounded-4 mb-5 shadow-inner">
                <div>
                  <p class="text-muted small mb-1">Total estimé</p>
                  <h3 class="mb-0 text-navy fw-bold">{{ montantTotal }} MRU</h3>
                </div>
                <div class="text-end">
                  <p class="mb-0 fw-bold">{{ chambreSelectionnee.type }}</p>
                  <p class="text-muted small mb-0">Chambre n°{{ chambreSelectionnee.numero }}</p>
                </div>
              </div>

              <button class="btn btn-accent w-100 py-4 fs-5 shadow-lg rounded-pill" [disabled]="!reservation.dateArrivee || !reservation.dateDepart || isProcessing" (click)="confirmerReservation()">
                <span *ngIf="!isProcessing">Confirmer ma réservation <i class="bi bi-check-lg ms-2"></i></span>
                <span *ngIf="isProcessing" class="spinner-border spinner-border-sm"></span>
              </button>
            </div>
          </div>
        </div>

        <!-- Écran de Paiement Bankily -->
        <div *ngIf="reservationCreee" class="row justify-content-center animate-fade-in">
          <div class="col-lg-6">
            <div class="glass-card p-5 border-0 shadow-lg text-center" style="border-radius: 30px; border-top: 5px solid #198754 !important;">
              <div class="mb-4">
                <div class="bg-success-subtle text-success rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                  <i class="bi bi-shield-check fs-1"></i>
                </div>
                <h2 class="font-display">Paiement Bankily</h2>
                <p class="text-muted">Votre réservation est prête. Finalisez le paiement pour la confirmer.</p>
              </div>

              <div class="mb-4 text-start">
                <label class="form-label small fw-bold text-uppercase tracking-wider">Numéro Bankily</label>
                <div class="input-group input-group-lg">
                  <span class="input-group-text bg-white border-0 shadow-sm"><i class="bi bi-phone"></i></span>
                  <input type="text" class="form-control border-0 shadow-sm" [(ngModel)]="bankilyPhone" placeholder="Ex: 44123456" style="border-radius: 0 12px 12px 0;">
                </div>
              </div>

              <div class="p-3 bg-light rounded-3 mb-4 d-flex justify-content-between">
                <span>Montant à régler</span>
                <span class="fw-bold">{{ montantTotal }} MRU</span>
              </div>

              <button class="btn btn-success w-100 py-4 fs-5 shadow rounded-pill mb-3" [disabled]="!bankilyPhone || isProcessing" (click)="procederPaiement()">
                <span *ngIf="!isProcessing"><i class="bi bi-wallet2 me-2"></i> Payer maintenant</span>
                <span *ngIf="isProcessing" class="spinner-border spinner-border-sm"></span>
              </button>

              <button class="btn btn-link text-muted text-decoration-none small" (click)="reinitialiser()">Annuler et revenir à l'accueil</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .font-display { font-family: 'Cormorant Garamond', serif; font-weight: 700; }
    .bg-navy { background-color: #1a1e26; }
    .text-gold { color: #c5a059; }
    .btn-navy { background-color: #1a1e26; color: white; transition: all 0.3s; }
    .btn-navy:hover { background-color: #2c3441; transform: translateY(-2px); }
    .card-hover:hover { transform: translateY(-10px); transition: transform 0.3s; }
    .bg-gold { background-color: #c5a059; }
    .text-navy { color: #1a1e26; }
    .animate-fade-in { animation: fadeIn 0.5s ease-out; }
    .shadow-inner { box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  `]
})
export class AccueilClientComponent implements OnInit {
  chambres: any[] = [];
  chambreSelectionnee: any = null;
  reservationCreee: any = null;
  reservation = { dateArrivee: '', dateDepart: '', clientId: '' };
  currentUser: any = null;
  montantTotal = 0;
  bankilyPhone = '';
  isProcessing = false;

  constructor(
    private chambreService: ChambreService, 
    private resService: ReservationService,
    private paiementService: PaiementService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Récupérer l'utilisateur connecté
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.reservation.clientId = user ? user.nom || user.email : 'Client';
    });

    this.chambreService.getChambres().subscribe(data => {
      this.chambres = data.filter(c => c.etat === 'disponible').map(c => ({
        ...c,
        image: c.image && c.image.startsWith('http') ? c.image : 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=800'
      }));
    });
  }

  selectionnerChambre(chambre: any) {
    this.chambreSelectionnee = chambre;
    this.calculerTotal();
  }

  calculerTotal() {
    if (this.chambreSelectionnee && this.reservation.dateArrivee && this.reservation.dateDepart) {
      const start = new Date(this.reservation.dateArrivee);
      const end = new Date(this.reservation.dateDepart);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      // On s'assure qu'au moins 1 jour est compté
      const diffDays = Math.max(1, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
      this.montantTotal = diffDays * this.chambreSelectionnee.prixParNuit;
    } else {
      this.montantTotal = this.chambreSelectionnee ? this.chambreSelectionnee.prixParNuit : 0;
    }
  }

  confirmerReservation() {
    this.isProcessing = true;
    const payload = {
      ...this.reservation,
      chambreId: this.chambreSelectionnee._id,
      montantTotal: this.montantTotal,
      statut: 'en_attente'
    };
    this.resService.createReservation(payload).subscribe({
      next: (res) => {
        this.reservationCreee = res;
        this.isProcessing = false;
      },
      error: (err) => {
        alert('Erreur : ' + (err.error?.message || 'Dates indisponibles'));
        this.isProcessing = false;
      }
    });
  }

  procederPaiement() {
    this.isProcessing = true;
    this.paiementService.payerBankily(this.reservationCreee._id, this.montantTotal, this.bankilyPhone).subscribe({
      next: () => {
        alert('Félicitations ! Votre paiement Bankily a été validé et votre suite est confirmée.');
        this.reinitialiser();
      },
      error: (err) => {
        alert('Le paiement n\'a pas pu être traité. Veuillez réessayer.');
        this.isProcessing = false;
      }
    });
  }

  reinitialiser() {
    this.chambreSelectionnee = null;
    this.reservationCreee = null;
    this.bankilyPhone = '';
    this.reservation = { dateArrivee: '', dateDepart: '', clientId: 'Client VIP' };
    this.isProcessing = false;
  }
}
