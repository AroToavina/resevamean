import { Injectable, ConflictException, NotFoundException, Inject } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { Reservation, ReservationDocument } from './schemas/reservation.schema';
import { Chambre, ChambreDocument } from '../chambres/schemas/chambre.schema';
import { ReservationsGateway } from './reservations/reservations.gateway';
import Redlock from 'redlock';

@Injectable()
export class ReservationsService {
  constructor(
    @InjectModel(Reservation.name) private reservationModel: Model<ReservationDocument>,
    @InjectModel(Chambre.name) private chambreModel: Model<ChambreDocument>,
    private readonly reservationsGateway: ReservationsGateway,
    @Inject('REDLOCK') private readonly redlock: Redlock,
    @Inject('REDIS_CLIENT') private readonly redisClient: any,
  ) {}

  private async clearCache() {
    if (!this.redisClient || !this.redisClient.isOpen) return;
    try {
      await this.redisClient.del('reservations:all');
    } catch (e) {
      console.error('Redis del error:', e);
    }
  }

  async create(createReservationDto: any): Promise<Reservation> {
    const { chambreId, dateArrivee, dateDepart } = createReservationDto;

    const resource = `locks:chambre:${chambreId}`;
    const ttl = 5000;

    let lock;
    const session = await this.reservationModel.db.startSession();

    try {
      session.startTransaction();
    } catch (e) {}

    try {
      // Vérifier si Redis est connecté avant d'utiliser Redlock
      if (this.redisClient && this.redisClient.isOpen) {
        lock = await this.redlock.acquire([resource], ttl);
      }

      const chambre = await this.chambreModel.findById(chambreId).session(session);
      if (!chambre) throw new NotFoundException('Chambre introuvable');
      
      if (chambre.etat === 'maintenance') {
        throw new ConflictException('La chambre est en maintenance.');
      }

      // Vérifier les chevauchements de dates
      const conflit = await this.reservationModel.findOne({
        chambreId: new Types.ObjectId(chambreId),
        statut: { $ne: 'annulee' },
        $or: [
          { dateArrivee: { $lt: new Date(dateDepart) }, dateDepart: { $gt: new Date(dateArrivee) } },
        ],
      }).session(session);

      if (conflit) {
        throw new ConflictException('Cette chambre est déjà réservée pour ces dates.');
      }

      const newReservation = new this.reservationModel({ 
        ...createReservationDto, 
        // Assurer un montant minimum si nécessaire
        montantTotal: createReservationDto.montantTotal > 0 ? createReservationDto.montantTotal : chambre.prixParNuit,
        statut: 'en_attente'
      });
      
      const saved = await newReservation.save({ session });
      await saved.populate('chambreId');
      
      await session.commitTransaction();
      
      await this.clearCache();
      this.reservationsGateway.notifyChangement('reservationCreated', saved);
      
      return saved;
    } catch (err) {
      if (session.inTransaction()) {
        await session.abortTransaction();
      }
      console.error('Détail de l\'erreur de réservation:', err);
      
      if (err instanceof ConflictException || err instanceof NotFoundException) throw err;
      throw new ConflictException(`Erreur : ${err.message || 'Problème technique lors de la réservation'}`);
    } finally {
      session.endSession();
      if (lock) await lock.release();
    }
  }

  async findAll(): Promise<Reservation[]> {
    const cacheKey = 'reservations:all';
    
    if (this.redisClient && this.redisClient.isOpen) {
      try {
        const cached = await this.redisClient.get(cacheKey);
        if (cached) return JSON.parse(cached);
      } catch (e) {
        console.error('Redis error:', e);
      }
    }

    const reservations = await this.reservationModel.find().populate('chambreId').sort({ createdAt: -1 }).exec();
    
    if (this.redisClient && this.redisClient.isOpen) {
      try {
        await this.redisClient.set(cacheKey, JSON.stringify(reservations), { EX: 60 });
      } catch (e) {
        console.error('Redis set error:', e);
      }
    }

    return reservations;
  }

  async findOne(id: string): Promise<Reservation> {
    const res = await this.reservationModel.findById(id).populate('chambreId').exec();
    if (!res) throw new NotFoundException('Réservation introuvable');
    return res;
  }

  async update(id: string, updateDto: any): Promise<Reservation> {
    const { __v, ...data } = updateDto;
    
    // Utilisation de findOneAndUpdate avec vérification de version pour l'Optimistic Locking
    const filter: any = { _id: id };
    if (__v !== undefined) filter.__v = __v;

    const updated = await this.reservationModel.findOneAndUpdate(
      filter,
      { $set: data, $inc: { __v: 1 } },
      { new: true, runValidators: true }
    ).populate('chambreId').exec();

    if (!updated) {
      throw new ConflictException('La réservation a été modifiée par un autre utilisateur ou est introuvable.');
    }

    await this.clearCache();
    this.reservationsGateway.notifyChangement('reservationUpdated', updated);
    return updated;
  }

  async delete(id: string): Promise<any> {
    const result = await this.reservationModel.findByIdAndDelete(id).exec();
    await this.clearCache();
    this.reservationsGateway.notifyChangement('reservationDeleted', { id });
    return result;
  }
}
