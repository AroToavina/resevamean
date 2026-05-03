pipeline {
    agent any

    environment {
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
                // Scan du dossier actuel
                sh 'docker run --rm -v $(pwd):/root/.cache/ aquasec/trivy:latest fs . --severity HIGH,CRITICAL'
            }
        }

        stage('Build des Images Docker') {
            steps {
                echo 'Construction des images...'
                sh 'docker build -t ${BACKEND_IMAGE}:latest ./backend'
                sh 'docker build -t ${FRONTEND_IMAGE}:latest ./frontend'
                sh 'docker build -t ${DJANGO_IMAGE}:latest ./reservation_hotel'
            }
        }

        stage('Scan des Images (Container Scanning)') {
            steps {
                echo 'Vérification des vulnérabilités dans les images construites...'
                sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${BACKEND_IMAGE}:latest"
            }
        }

        stage('Déploiement en Staging') {
            steps {
                echo 'Lancement des services via Docker Compose...'
                sh 'docker compose up -d'
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
