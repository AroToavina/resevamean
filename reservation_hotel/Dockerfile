FROM python:3.11-slim

# Empêche Python de générer des fichiers .pyc et d'utiliser un buffer pour les logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY README.md ./
# Note : Si ta copine a un requirements.txt, utilise-le. Sinon, on installe Django manuellement.
RUN pip install --no-cache-dir django gunicorn

COPY . .

EXPOSE 8000

# Utilisation de Gunicorn pour la production (plus robuste que manage.py runserver)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hotel_reservation.wsgi:application"]
