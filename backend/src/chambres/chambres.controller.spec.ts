import { Test, TestingModule } from '@nestjs/testing';
import { ChambresController } from './chambres.controller';

describe('ChambresController', () => {
  let controller: ChambresController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ChambresController],
    }).compile();

    controller = module.get<ChambresController>(ChambresController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
