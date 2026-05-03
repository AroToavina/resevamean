import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { ReservationService } from '../../services/reservation.service';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  currentUser: any = null;
  stats = [
    { label: "Réservations", value: "0", change: "+12.4%", icon: "bi-calendar-check" },
    { label: "Taux occupation", value: "0%", change: "+4.2%", icon: "bi-door-open" },
    { label: "Revenus (mois)", value: "0 MRU", change: "+8.1%", icon: "bi-currency-euro" },
    { label: "Nouveaux clients", value: "0", change: "+18%", icon: "bi-people" },
  ];

  recentReservations: any[] = [];
  allUsers: any[] = [];
  hasNewNotification = false;

  constructor(
    private reservationService: ReservationService,
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => this.currentUser = user);
    this.loadData();
    this.loadUsers();
    this.reservationService.getUpdates().subscribe((update: any) => {
      if (update.type === 'create') {
        this.hasNewNotification = true;
        this.loadData();
      }
    });
  }

  clearNotifications() {
    this.hasNewNotification = false;
  }

  loadUsers() {
    this.authService.getUsers().subscribe(users => {
      this.allUsers = users;
      this.cdr.markForCheck();
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  goToCalendar() {
    this.router.navigate(['/calendrier']);
  }

  loadData() {
    this.reservationService.getReservations().subscribe({
      next: (data) => {
        this.recentReservations = data;
        const totalRes = data.length;
        const revenue = data
          .filter(r => r.statut === 'confirmee')
          .reduce((acc, curr) => acc + (curr.montantTotal || 0), 0);
        const occupancy = data.length > 0 ? Math.min(Math.round((data.length / 20) * 100), 100) : 0;
        const clients = new Set(data.map(r => r.clientId)).size;

        this.stats[0].value = totalRes.toString();
        this.stats[1].value = occupancy + "%";
        this.stats[2].value = revenue.toLocaleString() + " MRU";
        this.stats[3].value = clients.toString();
        this.cdr.markForCheck();
      },
      error: (err) => console.error('Erreur chargement réservations:', err)
    });
  }

  confirmerReservation(res: any) {
    this.reservationService.updateReservation(res._id, { ...res, statut: 'confirmee' }).subscribe(() => {
      this.loadData();
    });
  }

  annulerReservation(res: any) {
    if (confirm('Voulez-vous vraiment annuler cette réservation ?')) {
      this.reservationService.updateReservation(res._id, { ...res, statut: 'annulee' }).subscribe(() => {
        this.loadData();
      });
    }
  }

  payerBankily(resId: string, montant: number) {
    const telephone = prompt('Entrez votre numéro Bankily pour confirmer le paiement :');
    if (telephone) {
      this.http.post('http://localhost:3000/paiements/bankily', {
        reservationId: resId,
        montant: montant,
        telephone: telephone
      }).subscribe(() => {
        alert('Paiement Bankily réussi !');
        this.loadData();
      });
    }
  }
}
