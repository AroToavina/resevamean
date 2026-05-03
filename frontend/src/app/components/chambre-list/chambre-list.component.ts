import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChambreService } from '../../services/chambre.service';

@Component({
  selector: 'app-chambre-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container py-5">
      <h2 class="text-center mb-5" style="font-family:'Cormorant Garamond', serif; color: var(--navy);">Nos Chambres d'Exception</h2>
      <div class="row g-4">
        <div class="col-md-4" *ngFor="let chambre of chambres">
          <div class="card h-100 border-0 shadow-sm overflow-hidden" style="border-radius: 15px; transition: transform 0.3s;">
            <img [src]="chambre.image || 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&q=80&w=800'" 
                 class="card-img-top" [alt]="chambre.type" style="height: 200px; object-fit: cover;">
            <div class="card-body p-4 text-center">
              <h5 class="fw-bold mb-2">{{ chambre.type }}</h5>
              <p class="text-muted mb-3">Chambre n°{{ chambre.numero }}</p>
              <h4 class="mb-4" style="color: var(--gold);">{{ chambre.prixParNuit }} MRU <small class="text-muted fs-6">/ nuit</small></h4>
              <button class="btn btn-accent w-100 rounded-pill">Réserver maintenant</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChambreListComponent implements OnInit {
  chambres: any[] = [];

  constructor(
    private chambreService: ChambreService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadChambres();
  }

  loadChambres() {
    this.chambreService.getChambres().subscribe(data => {
      this.chambres = data;
      this.cdr.markForCheck();
    });
  }

  seedChambres() {
    const types = ['Simple', 'Double', 'Suite Deluxe'];
    const mockChambres = [
      { numero: '101', type: 'Simple', prixParNuit: 2500, etat: 'disponible' },
      { numero: '102', type: 'Simple', prixParNuit: 2500, etat: 'occupee' },
      { numero: '201', type: 'Double', prixParNuit: 4500, etat: 'disponible' },
      { numero: '202', type: 'Double', prixParNuit: 4500, etat: 'maintenance' },
      { numero: '301', type: 'Suite Deluxe', prixParNuit: 8500, etat: 'disponible' }
    ];

    mockChambres.forEach(c => {
      this.chambreService.createChambre(c).subscribe(() => this.loadChambres());
    });
  }
}
