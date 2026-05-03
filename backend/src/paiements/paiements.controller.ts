import { Controller, Post, Body, Get, Param } from '@nestjs/common';
import { PaiementsService } from './paiements.service';

@Controller('paiements')
export class PaiementsController {
  constructor(private readonly paiementsService: PaiementsService) {}

  @Post('bankily')
  payWithBankily(@Body() payload: any) {
    return this.paiementsService.processBankily(payload);
  }

  @Get('reservation/:id')
  getByReservation(@Param('id') id: string) {
    return this.paiementsService.getPaiementsByReservation(id);
  }
}
