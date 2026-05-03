import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';
import * as dotenv from 'dotenv';

async function bootstrap() {
  // Charger le fichier .env manuellement pour main.ts
  dotenv.config();
  
  const app = await NestFactory.create(AppModule);
  
  // Configuration CORS ultra-permissive pour le développement
  app.enableCors({
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    allowedHeaders: 'Content-Type, Accept, Authorization',
    credentials: true,
  });
  
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
  }));

  const port = process.env.PORT || 3000;
  // Écouter sur toutes les interfaces pour éviter les problèmes IPv6/IPv4
  await app.listen(port, '0.0.0.0');
  console.log(`Le serveur est lancé sur : http://localhost:${port}`);
}
bootstrap();
