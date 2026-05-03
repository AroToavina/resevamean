# Versions des Technologies et Frameworks

Ce document liste les versions des technologies, frameworks et dépendances principales utilisées dans ce projet MEAN (MongoDB, Express/NestJS, Angular, Node.js).

## 1. Backend (NestJS)
- **Framework :** [NestJS](https://nestjs.com/) `^11.0.1`
- **Langage :** TypeScript `^5.7.3`
- **Base de données :** [MongoDB](https://www.mongodb.com/) (via [Mongoose](https://mongoosejs.com/)) `^9.5.0`
- **Cache & Concurrence :** [Redis](https://redis.io/) `^5.12.1`, [Redlock](https://github.com/mike-marcacci/node-redlock) `^5.0.0-beta.2`
- **Authentification :** [JWT](https://jwt.io/) (`@nestjs/jwt` `^11.0.2`, `passport-jwt` `^4.0.1`)
- **Validation :** `class-validator` `^0.15.1`, `class-transformer` `^0.5.1`

## 2. Frontend (Angular)
- **Framework :** [Angular](https://angular.dev/) `18.2.21`
- **Langage :** TypeScript `~5.5.2`
- **Design :** [Bootstrap](https://getbootstrap.com/) `5.3.3`
- **Composants :** [FullCalendar](https://fullcalendar.io/) (via `@fullcalendar/angular`) `6.1.15`

## 3. Environnement de Développement
- **Runtime :** Node.js `^22.10.7` (Type)
- **Outils :** 
  - [Jest](https://jestjs.io/) (Tests) `^30.0.0`
  - [ESLint](https://eslint.org/) `^9.18.0`
  - [Prettier](https://prettier.io/) `^3.4.2`

*Note : Les dépendances complètes et les versions précises sont disponibles dans les fichiers `package.json` de chaque répertoire (`/backend/package.json` et `/frontend/package.json`).*
