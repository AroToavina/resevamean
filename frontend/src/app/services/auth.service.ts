import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:3000/auth';
  private currentUserSubject = new BehaviorSubject<any>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    const token = this.getToken();
    if (token) {
      // Pour simplifier on stocke l'utilisateur en local, 
      // idéalement on décoderait le JWT ici.
      const user = JSON.parse(localStorage.getItem('user') || 'null');
      this.currentUserSubject.next(user);
    }
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData);
  }

  login(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/login`, credentials).pipe(
      tap((res: any) => {
        if (res.access_token) {
          this.saveToken(res.access_token);
          this.currentUserSubject.next(res.user);
          localStorage.setItem('user', JSON.stringify(res.user));
        }
      })
    );
  }

  saveToken(token: string) {
    localStorage.setItem('token', token);
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/users`);
  }

  updateUser(id: string, userData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${id}`, userData).pipe(
      tap((updatedUser: any) => {
        // Mettre à jour l'utilisateur local si c'est l'utilisateur courant
        const current = this.currentUserSubject.value;
        if (current && current.id === id) {
          const newUser = { ...current, ...updatedUser };
          this.currentUserSubject.next(newUser);
          localStorage.setItem('user', JSON.stringify(newUser));
        }
      })
    );
  }

  logout() {
    localStorage.clear(); // Nettoie tout
    this.currentUserSubject.next(null);
  }
}
