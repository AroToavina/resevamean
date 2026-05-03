import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ChambreDocument = Chambre & Document;

@Schema({ timestamps: true })
export class Chambre {
  @Prop({ required: true, unique: true })
  numero: string;

  @Prop({ required: true })
  type: string; // ex: Simple, Double, Suite

  @Prop({ required: true })
  prixParNuit: number;

  @Prop({ default: 'disponible', enum: ['disponible', 'occupee', 'maintenance'] })
  etat: string;

  @Prop({ default: [] })
  equipements: string[];

  @Prop()
  description: string;

  @Prop()
  image: string;
}

export const ChambreSchema = SchemaFactory.createForClass(Chambre);
