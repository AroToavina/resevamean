import { Test, TestingModule } from '@nestjs/testing';
import { ReservationsGateway } from './reservations.gateway';

describe('ReservationsGateway', () => {
  let gateway: ReservationsGateway;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [ReservationsGateway],
    }).compile();

    gateway = module.get<ReservationsGateway>(ReservationsGateway);
  });

  it('should be defined', () => {
    expect(gateway).toBeDefined();
  });
});
