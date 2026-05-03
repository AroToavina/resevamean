import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Paiement, PaiementDocument } from './schemas/paiement.schema';
import { ReservationsService } from '../reservations/reservations.service';

@Injectable()
export class PaiementsService {
  constructor(
    @InjectModel(Paiement.name) private paiementModel: Model<PaiementDocument>,
    private readonly reservationsService: ReservationsService,
  ) {}

  async processBankily(payload: any): Promise<Paiement> {
    const { reservationId, montant, telephone } = payload;

    // Vérifier la réservation
    const reservation = await this.reservationsService.findOne(reservationId);
    if (!reservation) throw new NotFoundException('Réservation introuvable');
    
    // Vérifier si le montant correspond (optionnel mais recommandé)
    if (reservation.montantTotal > montant) {
       // On pourrait lever une erreur ou accepter un paiement partiel
    }

    // Simulation de l'appel API Bankily
    // Dans un cas réel, on appellerait un service externe ici
    const isSuccess = true; 
    const transactionId = `BNK-${Date.now()}-${Math.random().toString(36).substring(7).toUpperCase()}`;

    const newPaiement = new this.paiementModel({
      reservationId,
      montant,
      methode: 'bankily',
      statut: isSuccess ? 'reussi' : 'echoue',
      transactionId,
      telephoneClient: telephone,
      datePaiement: new Date()
    });
    
    const savedPaiement = await newPaiement.save();

    if (isSuccess) {
      // Mise à jour atomique du statut de la réservation
      await this.reservationsService.update(reservationId, { 
        statut: 'confirmee',
        __v: (reservation as any).__v // Utilisation du verrouillage optimiste
      });
    }

    return savedPaiement;
  }

  async getPaiementsByReservation(resId: string): Promise<Paiement[]> {
    return this.paiementModel.find({ reservationId: resId }).exec();
  }
}
