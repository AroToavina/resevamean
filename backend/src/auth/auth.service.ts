import { Injectable, ConflictException, OnModuleInit } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { User, UserDocument } from './schemas/user.schema';

@Injectable()
export class AuthService implements OnModuleInit {
  constructor(
    @InjectModel(User.name) private userModel: Model<UserDocument>,
    private jwtService: JwtService,
  ) {}

  async onModuleInit() {
    const adminEmail = 'admin@maisonroyale.com';
    const userEmail = 'tsantapriscilla'; // ou votre email complet si c'est une adresse

    // Rectifier l'Admin
    await this.userModel.updateOne({ email: adminEmail }, { $set: { role: 'admin' } });
    
    // Rectifier l'Utilisateur (utilisez l'email complet ici)
    await this.userModel.updateOne({ email: 'tsantapriscilla' }, { $set: { role: 'user' } });

    console.log('Rôles utilisateurs synchronisés avec succès.');
  }

  async findAll(): Promise<User[]> {
    return this.userModel.find().select('-password').exec();
  }

  async update(id: string, updateDto: any): Promise<User> {
    const user = await this.userModel.findByIdAndUpdate(id, { $set: updateDto }, { new: true }).select('-password').exec();
    if (!user) throw new ConflictException('Utilisateur introuvable');
    return user;
  }

  async register(registerDto: any): Promise<User> {
    const { email, password, nom } = registerDto;
    
    const existingUser = await this.userModel.findOne({ email }).exec();
    if (existingUser) {
      throw new ConflictException('Cet email est déjà utilisé');
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new this.userModel({ email, password: hashedPassword, nom, role: 'user' });
    return newUser.save();
  }

  async login(loginDto: any) {
    const { email, password } = loginDto;
    const user = await this.userModel.findOne({ email }).exec();
    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new ConflictException('Email ou mot de passe incorrect');
    }
    const payload = { email: user.email, sub: user._id, role: user.role };
    return {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user._id,
        email: user.email,
        nom: user.nom,
        role: user.role
      }
    };
  }
}
