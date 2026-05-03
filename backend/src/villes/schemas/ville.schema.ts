import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

@Schema()
export class Ville extends Document {
  @Prop({ required: true })
  nom: string;
}

export const VilleSchema = SchemaFactory.createForClass(Ville);
