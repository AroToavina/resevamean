import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ChambresService } from './chambres.service';

@Controller('chambres')
export class ChambresController {
  constructor(private readonly chambresService: ChambresService) {}

  @Post()
  create(@Body() createDto: any) {
    return this.chambresService.create(createDto);
  }

  @Get()
  findAll() {
    return this.chambresService.findAll();
  }

  @Get('search')
  search(@Query('ville') ville: string, @Query('dateArrivee') dateArrivee: string, @Query('dateDepart') dateDepart: string) {
    return this.chambresService.search(ville, new Date(dateArrivee), new Date(dateDepart));
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.chambresService.findOne(id);
  }
}
