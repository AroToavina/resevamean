import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChambreService {
  private apiUrl = 'http://localhost:3000/chambres';

  constructor(private http: HttpClient) {}

  getChambres(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  createChambre(chambre: any): Observable<any> {
    console.log('Envoi vers API:', chambre);
    return this.http.post<any>(this.apiUrl, chambre).pipe(
      tap(res => console.log('Réponse API:', res))
    );
  }
}
