import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FullCalendarModule } from '@fullcalendar/angular';
import { CalendarOptions } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { ReservationService } from '../../services/reservation.service';
import { ReservationFormComponent } from '../reservation-form/reservation-form.component';

@Component({
  selector: 'app-calendrier-reservations',
  standalone: true,
  imports: [CommonModule, FullCalendarModule, ReservationFormComponent],
  template: `
    <div class="container-fluid py-4 fade-in">
      <div class="row g-4">
        <div class="col-xl-8 col-lg-7">
          <div class="glass-card p-4 border-0 h-100">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h4 class="fw-bold m-0" style="font-family: 'Cormorant Garamond', serif;">Planning des Occupations</h4>
              <div class="d-flex gap-2">
                <span class="badge bg-success-subtle text-success border border-success rounded-pill px-3">Confirmée</span>
                <span class="badge bg-warning-subtle text-warning border border-warning rounded-pill px-3">En attente</span>
              </div>
            </div>
            <full-calendar [options]="calendarOptions"></full-calendar>
          </div>
        </div>
        <div class="col-xl-4 col-lg-5">
          <app-reservation-form class="h-100"></app-reservation-form>
        </div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CalendrierReservationsComponent implements OnInit {
  calendarOptions: CalendarOptions = {
    initialView: 'dayGridMonth',
    plugins: [dayGridPlugin, interactionPlugin],
    events: [],
    height: 'auto',
    locale: 'fr',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,dayGridWeek'
    },
    eventClick: this.handleEventClick.bind(this),
    eventDisplay: 'block',
  };

  constructor(
    private reservationService: ReservationService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadReservations();
    this.listenToUpdates();
  }

  loadReservations() {
    this.reservationService.getReservations().subscribe(data => {
      this.calendarOptions.events = data.map(res => ({
        id: res._id,
        title: `Ch. ${res.chambreId?.numero || res.chambreId} - ${res.clientId}`,
        start: res.dateArrivee,
        end: res.dateDepart,
        backgroundColor: res.statut === 'confirmee' ? '#198754' : '#ffc107',
        borderColor: 'transparent',
        textColor: res.statut === 'confirmee' ? '#ffffff' : '#000000',
        extendedProps: { ...res }
      }));
      this.calendarOptions = { ...this.calendarOptions };
      this.cdr.markForCheck();
    });
  }

  listenToUpdates() {
    this.reservationService.getUpdates().subscribe(() => this.loadReservations());
  }

  handleEventClick(arg: any) {
    const res = arg.event.extendedProps;
    alert(`Détails Réservation :\nClient : ${res.clientId}\nChambre : ${res.chambreId?.numero}\nStatut : ${res.statut}`);
  }
}
