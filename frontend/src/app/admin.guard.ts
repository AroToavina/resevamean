import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from './services/auth.service';

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  // Autoriser l'accès si c'est un admin
  if (authService.isLoggedIn() && user.role === 'admin') {
    return true;
  }
  
  // Sinon, renvoyer vers l'accueil ou le login
  router.navigate(['/login']);
  return false;
};
