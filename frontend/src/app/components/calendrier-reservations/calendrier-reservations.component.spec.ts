import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CalendrierReservationsComponent } from './calendrier-reservations.component';

describe('CalendrierReservationsComponent', () => {
  let component: CalendrierReservationsComponent;
  let fixture: ComponentFixture<CalendrierReservationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CalendrierReservationsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CalendrierReservationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
