import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HotelService {
  private apiUrl = 'http://localhost:3000'; // Assurez-vous que le backend tourne sur ce port

  constructor(private http: HttpClient) {}

  getVilles(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/villes`);
  }
}
