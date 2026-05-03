import { Test, TestingModule } from '@nestjs/testing';
import { VillesController } from './villes.controller';

describe('VillesController', () => {
  let controller: VillesController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [VillesController],
    }).compile();

    controller = module.get<VillesController>(VillesController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
