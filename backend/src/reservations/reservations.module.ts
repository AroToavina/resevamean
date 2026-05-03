import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ReservationsController } from './reservations.controller';
import { ReservationsService } from './reservations.service';
import { Reservation, ReservationSchema } from './schemas/reservation.schema';
import { Chambre, ChambreSchema } from '../chambres/schemas/chambre.schema';
import { ReservationsGateway } from './reservations/reservations.gateway';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: Reservation.name, schema: ReservationSchema },
      { name: Chambre.name, schema: ChambreSchema }
    ]),
  ],
  controllers: [ReservationsController],
  providers: [ReservationsService, ReservationsGateway],
  exports: [ReservationsService],
})
export class ReservationsModule {}
