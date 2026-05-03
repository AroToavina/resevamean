import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PaiementService {
  private apiUrl = 'http://localhost:3000/paiements';

  constructor(private http: HttpClient) {}

  payerBankily(reservationId: string, montant: number, telephone: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/bankily`, {
      reservationId,
      montant,
      telephone
    });
  }

  getHistorique(reservationId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/reservation/${reservationId}`);
  }
}
