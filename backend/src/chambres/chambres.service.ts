import { Injectable, NotFoundException, OnModuleInit } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Chambre, ChambreDocument } from './schemas/chambre.schema';

@Injectable()
export class ChambresService implements OnModuleInit {
  constructor(@InjectModel(Chambre.name) private chambreModel: Model<ChambreDocument>) {}

  async onModuleInit() {
    const count = await this.chambreModel.countDocuments();
    const defaultChambres = [
      { 
        numero: '101', 
        type: 'Suite Royale', 
        prixParNuit: 12000, 
        etat: 'disponible', 
        description: 'Une suite majestueuse avec vue sur mer, salon privé et service de majordome.',
        image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&q=80&w=800'
      },
      { 
        numero: '102', 
        type: 'Suite Junior', 
        prixParNuit: 8500, 
        etat: 'disponible', 
        description: 'Élégance et confort moderne pour vos séjours d\'affaires ou de détente.',
        image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=800'
      },
      { 
        numero: '201', 
        type: 'Chambre Deluxe', 
        prixParNuit: 5500, 
        etat: 'disponible', 
        description: 'Le luxe abordable avec une literie de haute qualité et une décoration raffinée.',
        image: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&q=80&w=800'
      },
      { 
        numero: '301', 
        type: 'Penthouse', 
        prixParNuit: 25000, 
        etat: 'disponible', 
        description: 'L\'expérience ultime avec terrasse panoramique, jacuzzi privé et accès VIP.',
        image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800'
      }
    ];

    if (count === 0) {
      console.log('Initialisation des chambres...');
      await this.chambreModel.insertMany(defaultChambres);
    } else {
      console.log('Mise à jour forcée des images et descriptions...');
      for (const def of defaultChambres) {
        await this.chambreModel.updateOne(
          { numero: def.numero },
          { $set: { image: def.image, description: def.description } }
        );
      }
    }
  }

  async create(createChambreDto: any): Promise<Chambre> {
    const newChambre = new this.chambreModel(createChambreDto);
    return newChambre.save();
  }

  async findAll(): Promise<Chambre[]> {
    return this.chambreModel.find().exec();
  }

  async search(ville: string, dateArrivee: Date, dateDepart: Date): Promise<Chambre[]> {
    // Note: Pour une implémentation réelle, il faudra filtrer les chambres
    // qui ne sont pas déjà réservées sur la période.
    // Ici, nous commençons par une recherche simple par état 'disponible'.
    return this.chambreModel.find({ etat: 'disponible' }).exec();
  }

  async findOne(id: string): Promise<Chambre> {
    const chambre = await this.chambreModel.findById(id).exec();
    if (!chambre) throw new NotFoundException('Chambre introuvable');
    return chambre;
  }
}
