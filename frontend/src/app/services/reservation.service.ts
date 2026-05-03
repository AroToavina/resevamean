import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class ReservationService {
  private apiUrl = 'http://localhost:3000/reservations';
  private socket: Socket;
  private reservationUpdates = new Subject<any>();

  constructor(private http: HttpClient) {
    // Connexion au serveur WebSocket de NestJS sur le port 3000
    this.socket = io('http://localhost:3000');
    
    // Écoute des événements en temps réel
    this.socket.on('reservationCreated', (data) => {
      this.reservationUpdates.next({ type: 'create', data });
    });
    
    this.socket.on('reservationUpdated', (data) => {
      this.reservationUpdates.next({ type: 'update', data });
    });
    
    this.socket.on('reservationDeleted', (data) => {
      this.reservationUpdates.next({ type: 'delete', data });
    });
  }

  // API REST
  getReservations(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  createReservation(reservation: any): Observable<any> {
    return this.http.post<any>(this.apiUrl, reservation);
  }

  updateReservation(id: string, reservation: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, reservation);
  }

  // Observable pour les mises à jour en temps réel
  getUpdates() {
    return this.reservationUpdates.asObservable();
  }
}
