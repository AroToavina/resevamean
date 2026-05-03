import { Controller, Get, Post, Put, Body, Param } from '@nestjs/common';
import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  login(@Body() loginDto: any) {
    return this.authService.login(loginDto);
  }

  @Get('users')
  findAll() {
    return this.authService.findAll();
  }

  @Put('users/:id')
  update(@Param('id') id: string, @Body() updateDto: any) {
    return this.authService.update(id, updateDto);
  }

  @Post('register')
  register(@Body() registerDto: any) {
    return this.authService.register(registerDto);
  }
}
