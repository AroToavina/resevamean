import { Module } from '@nestjs/common';
import { VillesController } from './villes.controller';
import { VillesService } from './villes.service';
import { MongooseModule } from '@nestjs/mongoose';
import { Ville, VilleSchema } from './schemas/ville.schema';

@Module({
  imports: [MongooseModule.forFeature([{ name: Ville.name, schema: VilleSchema }])],
  controllers: [VillesController],
  providers: [VillesService],
})
export class VillesModule {}

