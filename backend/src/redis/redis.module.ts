import { Module, Global } from '@nestjs/common';
import { createClient } from 'redis';
import Redlock from 'redlock';

@Global()
@Module({
  providers: [
    {
      provide: 'REDIS_CLIENT',
      useFactory: async () => {
        const client = createClient({ 
          url: process.env.REDIS_URL || 'redis://localhost:6379',
          socket: {
            reconnectStrategy: (retries) => {
              if (retries > 0) return false; // Stop après la première tentative
              return 500;
            }
          }
        });
        client.on('error', (err) => { /* Silence total après l'échec initial */ });
        try {
          await client.connect();
          console.log('Connecté à Redis avec succès');
        } catch (e) {
          console.log('NOTE: Redis est absent. Le verrouillage Redlock et le cache sont désactivés.');
        }
        return client;
      },
    },
    {
      provide: 'REDLOCK',
      inject: ['REDIS_CLIENT'],
      useFactory: (client) => {
        return new Redlock([client], {
          driftFactor: 0.01,
          retryCount: 10,
          retryDelay: 200,
          retryJitter: 200,
        });
      },
    },
  ],
  exports: ['REDIS_CLIENT', 'REDLOCK'],
})
export class RedisModule {}
