import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Ville } from './schemas/ville.schema';

@Injectable()
export class VillesService {
  constructor(@InjectModel(Ville.name) private villeModel: Model<Ville>) {}

  async findAll(): Promise<Ville[]> {
    return this.villeModel.find().exec();
  }
}
