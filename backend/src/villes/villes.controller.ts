import { Controller, Get } from '@nestjs/common';
import { VillesService } from './villes.service';

@Controller('villes')
export class VillesController {
  constructor(private readonly villesService: VillesService) {}

  @Get()
  findAll() {
    return this.villesService.findAll();
  }
}
