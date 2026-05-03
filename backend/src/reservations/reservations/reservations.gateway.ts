import {
  WebSocketGateway,
  SubscribeMessage,
  MessageBody,
  WebSocketServer,
  OnGatewayInit,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger } from '@nestjs/common';

@WebSocketGateway({
  cors: {
    origin: '*',
    methods: ["GET", "POST"],
    credentials: true
  },
  transports: ['polling', 'websocket']
})
export class ReservationsGateway implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer() server: Server;
  private logger: Logger = new Logger('ReservationsGateway');

  @SubscribeMessage('checkDisponibilite')
  handleMessage(@MessageBody() data: any): void {
    // Logique pour vérifier la disponibilité en temps réel si besoin
    this.server.emit('disponibiliteChecked', { status: 'ok', data });
  }

  // Méthode pour notifier tous les clients d'un changement
  notifyChangement(event: string, payload: any) {
    this.server.emit(event, payload);
  }

  afterInit(server: Server) {
    this.logger.log('Init WebSocket Server');
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  handleConnection(client: Socket, ...args: any[]) {
    this.logger.log(`Client connected: ${client.id}`);
  }
}
