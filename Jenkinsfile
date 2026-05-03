pipeline {
    agent any

    environment {
        // Définition des noms d'images
        BACKEND_IMAGE = "resevamean-backend"
        FRONTEND_IMAGE = "resevamean-frontend"
        DJANGO_IMAGE = "resevamean-django"
    }

    stages {
        stage('Clonage du Projet') {
            steps {
                checkout scm
            }
        }

        stage('Analyse Statique (SAST) avec Trivy') {
            steps {
                echo 'Analyse du code source pour détecter des secrets ou vulnérabilités...'
                // Scan du dossier actuel (fs = filesystem)
                sh 'docker run --rm -v $(pwd):/root/.cache/ aquasec/trivy:latest fs . --severity HIGH,CRITICAL'[cite: 2]
            }
        }

        stage('Build des Images Docker') {
            steps {
                echo 'Construction des images selon les spécifications TECH_VERSIONS...'[cite: 1]
                sh 'docker build -t ${BACKEND_IMAGE}:latest ./backend'
                sh 'docker build -t ${FRONTEND_IMAGE}:latest ./frontend'
                sh 'docker build -t ${DJANGO_IMAGE}:latest ./reservation_hotel'
            }
        }

        stage('Scan des Images (Container Scanning)') {
            steps {
                echo 'Vérification des vulnérabilités dans les images construites...'
                // On scanne l'image Backend (NestJS ^11.0.1 / Node 22.10.7)
                sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${BACKEND_IMAGE}:latest"[cite: 2]
            }
        }

        stage('Déploiement en Staging') {
            steps {
                echo 'Lancement des services via Docker Compose...'
                // Utilisation du docker-compose applicatif que tu as créé
                sh 'docker compose up -d'[cite: 2]
            }
        }
    }

    post {
        always {
            echo 'Nettoyage des images intermédiaires...'
            sh 'docker image prune -f'
        }
    }
}
