import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type ReservationDocument = Reservation & Document;

@Schema({ 
  timestamps: true,
  optimisticConcurrency: true,
  versionKey: '__v'
})
export class Reservation {
  @Prop({ required: true })
  dateArrivee: Date;

  @Prop({ required: true })
  dateDepart: Date;

  @Prop({ type: Types.ObjectId, ref: 'Chambre', required: true })
  chambreId: Types.ObjectId;

  @Prop({ required: true })
  clientId: string;

  @Prop({ 
    required: true, 
    enum: ['en_attente', 'confirmee', 'checkin', 'checkout', 'annulee'],
    default: 'en_attente'
  })
  statut: string;

  @Prop({ default: 0 })
  montantTotal: number;

  @Prop({ default: 1 })
  nbrAdultes: number;

  @Prop({ default: 0 })
  nbrEnfants: number;
}

export const ReservationSchema = SchemaFactory.createForClass(Reservation);
