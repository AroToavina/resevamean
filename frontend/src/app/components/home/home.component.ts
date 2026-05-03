import { Component, OnInit } from '@angular/core';
import { HotelService } from '../../services/hotel.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  villes: any[] = [];
  currentUser: any = null;
  searchData = {
    ville: '',
    dateArrivee: '',
    dateDepart: '',
    adultes: 1
  };

  constructor(private hotelService: HotelService, private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => this.currentUser = user);
    this.hotelService.getVilles().subscribe(data => {
      this.villes = data;
    });
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  onSearch(): void {
    console.log('Recherche avec:', this.searchData);
    // Ici nous appellerons le service de recherche
  }
}
