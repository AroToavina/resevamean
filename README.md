# ResevaMEAN

Ce dépôt regroupe plusieurs applications autour d'un même domaine métier de réservation hôtelière. Il ne s'agit pas d'un projet unique homogène, mais d'un workspace contenant :

- un backend API en `NestJS` dans `backend/`
- un frontend SPA en `Angular` dans `frontend/`
- une application web complète en `Django` dans `reservation_hotel/`
- une orchestration Docker partielle à la racine via `docker-compose.yml`

## Vue d'ensemble

Le projet couvre les usages suivants :

- gestion des chambres
- gestion des réservations
- authentification utilisateur
- suivi des paiements
- gestion des villes et hôtels
- interface d'administration et espace client

## Structure

```text
.
├── backend/             # API NestJS + MongoDB + Redis optionnel
├── frontend/            # Application Angular consommant l'API NestJS
├── reservation_hotel/   # Application Django autonome
├── docker-compose.yml   # Compose pour frontend + backend + Django + Mongo
└── TECH_VERSIONS.md     # Versions principales des technos JS
```

## Architecture observée

### 1. Backend `backend/`

Stack :

- `NestJS 11`
- `TypeScript`
- `Mongoose` avec MongoDB
- `Redis` via `redis` et `redlock`
- `JWT` pour l'authentification
- `Socket.IO` pour des notifications temps réel

Modules principaux :

- `auth`
- `reservations`
- `chambres`
- `paiements`
- `villes`
- `redis`

API exposées dans le code :

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/users`
- `PUT /auth/users/:id`
- `GET /villes`
- `GET /chambres`
- `GET /chambres/search`
- `POST /chambres`
- `GET /reservations`
- `POST /reservations`
- `PUT /reservations/:id`
- `DELETE /reservations/:id`
- `POST /paiements/bankily`
- `GET /paiements/reservation/:id`

Temps réel :

- gateway Socket.IO sur le serveur NestJS
- écoute côté frontend de `reservationCreated`, `reservationUpdated`, `reservationDeleted`

Configuration importante relevée :

- port par défaut : `3000`
- variable attendue pour Mongo : `MONGODB_URI`
- variable optionnelle pour Redis : `REDIS_URL` avec fallback `redis://localhost:6379`
- secret JWT actuellement codé en dur dans `backend/src/auth/auth.module.ts`

### 2. Frontend `frontend/`

Stack :

- `Angular 18`
- `Bootstrap 5`
- `FullCalendar`
- `socket.io-client`

Routes principales :

- `/`
- `/login`
- `/register`
- `/accueil-client`
- `/dashboard`
- `/admin/clients`
- `/admin/settings`
- `/calendrier`
- `/chambres`
- `/profil`

Le frontend consomme directement l'API NestJS via des URLs codées en dur comme :

- `http://localhost:3000/auth`
- `http://localhost:3000/chambres`
- `http://localhost:3000/reservations`
- `http://localhost:3000/paiements`

Conséquence : en environnement Docker ou sur une autre machine, il faut adapter ces URLs ou ajouter un proxy.

### 3. Application Django `reservation_hotel/`

Cette partie est une application complète distincte de la stack NestJS/Angular.

Stack :

- `Python 3.11`
- `Django`
- `Gunicorn` dans l'image Docker
- `SQLite` comme base par défaut

Applications Django détectées :

- `ville`
- `hotel`
- `users`
- `client`
- `chambre`
- `services`
- `reservation`
- `paiement`

Fonctionnement observé :

- interface staff sur `/staff/`
- redirection racine vers `/client/`
- administration Django sur `/django-admin/`
- gestion des médias et statiques via Django

Attention :

- `DEBUG = False` dans `settings.py`
- `SECRET_KEY` est codée en dur
- la configuration utilise `SQLite`
- aucun `requirements.txt` ni `pyproject.toml` n'est versionné
- le code utilise des `ImageField`, donc `Pillow` sera probablement nécessaire hors image Docker

## Démarrage local

### Option A. Backend NestJS

Pré-requis :

- `Node.js 22`
- `npm`
- `MongoDB`
- `Redis` optionnel

Créer un fichier `backend/.env` minimal :

```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/resevamean
REDIS_URL=redis://localhost:6379
```

Lancer :

```bash
cd backend
npm install
npm run start:dev
```

Tests disponibles :

```bash
npm test
npm run test:e2e
```

### Option B. Frontend Angular

Pré-requis :

- `Node.js 22`
- backend NestJS disponible sur `http://localhost:3000`

Lancer :

```bash
cd frontend
npm install
npm start
```

Build :

```bash
npm run build
```

### Option C. Application Django

Pré-requis minimaux :

- `Python 3.11`
- `pip`

Comme les dépendances Python ne sont pas déclarées dans un fichier dédié, il faut au minimum installer :

```bash
cd reservation_hotel
pip install django gunicorn pillow
python manage.py migrate
python manage.py runserver
```

Application accessible ensuite sur `http://localhost:8000`.

## Démarrage Docker

Le fichier `docker-compose.yml` construit :

- `backend`
- `frontend`
- `reservation`
- `mongo`

Commande :

```bash
docker compose up --build
```

État actuel de cette orchestration :

- seul le frontend publie un port, `80:80`
- le backend NestJS n'expose pas `3000` vers l'hôte
- le service Django n'expose pas `8000` vers l'hôte
- aucun service Redis n'est défini
- aucune variable `MONGODB_URI` n'est fournie au backend

En l'état, le `docker-compose.yml` constitue une base de travail, mais pas une stack prête à l'emploi sans ajustements.

## Points d'attention techniques

- le dépôt mélange deux approches applicatives différentes : `NestJS/Angular` d'un côté et `Django` de l'autre
- plusieurs secrets ou paramètres sensibles sont codés en dur
- les URLs d'API du frontend sont figées sur `localhost:3000`
- la partie Django n'a pas de fichier de dépendances Python versionné
- des répertoires `__pycache__` et des médias sont présents dans le dépôt

## Fichiers utiles

- [docker-compose.yml](/home/xio/projet-devops/resevamean/docker-compose.yml)
- [TECH_VERSIONS.md](/home/xio/projet-devops/resevamean/TECH_VERSIONS.md)
- [backend/package.json](/home/xio/projet-devops/resevamean/backend/package.json)
- [frontend/package.json](/home/xio/projet-devops/resevamean/frontend/package.json)
- [reservation_hotel/hotel_reservation/settings.py](/home/xio/projet-devops/resevamean/reservation_hotel/hotel_reservation/settings.py)

## Résumé

Le dépôt contient une base fonctionnelle intéressante pour un système de réservation hôtelière, mais son état actuel ressemble davantage à un workspace de développement ou de formation qu'à une distribution unifiée prête pour la production. Le `README.md` racine sert donc surtout à clarifier l'architecture réelle, les commandes d'exécution et les écarts de configuration à corriger.
