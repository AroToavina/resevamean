# Étape 1 : Build de l'application Angular
FROM node:22-slim AS build
USER root
RUN apt-get update && apt-get upgrade -y && apt-get clean
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build -- --configuration=production

# Étape 2 : Serveur de production (Nginx)
FROM nginx:stable-alpine
# Copie des fichiers compilés depuis l'étape précédente
# Note : vérifie le nom du dossier dans frontend/dist/ (souvent le nom du projet)
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
