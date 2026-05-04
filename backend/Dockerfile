# --- Étape 1 : Build ---
FROM node:22-slim AS builder

USER root
RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances (y compris les devDependencies pour le build)
RUN npm install

# Copie du reste du code source
COPY . .

# Compilation du projet NestJS en JavaScript (dossier /dist)
RUN npm run build

# --- Étape 2 : Production ---
FROM node:22-slim

WORKDIR /app

# Copie uniquement des fichiers nécessaires à l'exécution
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

# Définition de l'utilisateur non-root pour la sécurité (bonne pratique DevSecOps)
USER node

# Le port par défaut de NestJS
EXPOSE 3000

CMD ["node", "dist/main"]
