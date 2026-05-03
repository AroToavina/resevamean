import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ChambresController } from './chambres.controller';
import { ChambresService } from './chambres.service';
import { Chambre, ChambreSchema } from './schemas/chambre.schema';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: Chambre.name, schema: ChambreSchema }]),
  ],
  controllers: [ChambresController],
  providers: [ChambresService],
  exports: [ChambresService],
})
export class ChambresModule {}
