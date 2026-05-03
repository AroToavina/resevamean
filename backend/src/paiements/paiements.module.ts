import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { PaiementsController } from './paiements.controller';
import { PaiementsService } from './paiements.service';
import { Paiement, PaiementSchema } from './schemas/paiement.schema';
import { ReservationsModule } from '../reservations/reservations.module';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: Paiement.name, schema: PaiementSchema }]),
    ReservationsModule, // Pour pouvoir mettre à jour le statut des réservations
  ],
  controllers: [PaiementsController],
  providers: [PaiementsService],
})
export class PaiementsModule {}
