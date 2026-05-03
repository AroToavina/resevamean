import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { CalendrierReservationsComponent } from './components/calendrier-reservations/calendrier-reservations.component';
import { ChambreListComponent } from './components/chambre-list/chambre-list.component';
import { ProfilClientComponent } from './components/profil-client/profil-client.component';
import { AccueilClientComponent } from './components/accueil-client/accueil-client.component';
import { RegisterComponent } from './components/auth/register.component';
import { UserListComponent } from './components/dashboard/user-list.component';
import { SettingsComponent } from './components/dashboard/settings.component';
import { adminGuard } from './admin.guard';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'accueil-client', component: AccueilClientComponent, canActivate: [authGuard] },
  { path: 'dashboard', component: DashboardComponent, canActivate: [adminGuard] },
  { path: 'admin/clients', component: UserListComponent, canActivate: [adminGuard] },
  { path: 'admin/settings', component: SettingsComponent, canActivate: [adminGuard] },
  { path: 'calendrier', component: CalendrierReservationsComponent, canActivate: [adminGuard] },
  { path: 'chambres', component: ChambreListComponent },
  { path: 'profil', component: ProfilClientComponent, canActivate: [authGuard] },
];
