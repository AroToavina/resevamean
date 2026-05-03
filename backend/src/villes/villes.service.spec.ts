import { Test, TestingModule } from '@nestjs/testing';
import { VillesService } from './villes.service';

describe('VillesService', () => {
  let service: VillesService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [VillesService],
    }).compile();

    service = module.get<VillesService>(VillesService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
