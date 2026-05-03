import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type PaiementDocument = Paiement & Document;

@Schema({ timestamps: true })
export class Paiement {
  @Prop({ type: Types.ObjectId, ref: 'Reservation', required: true })
  reservationId: Types.ObjectId;

  @Prop({ required: true })
  montant: number;

  @Prop({ required: true, enum: ['bankily', 'carte', 'especes'], default: 'bankily' })
  methode: string;

  @Prop({ required: true, enum: ['en_attente', 'reussi', 'echoue'], default: 'en_attente' })
  statut: string;

  @Prop()
  transactionId: string; // ID venant du fournisseur de paiement (ex: Bankily)

  @Prop()
  telephoneClient: string; // Utile pour Bankily
}

export const PaiementSchema = SchemaFactory.createForClass(Paiement);
