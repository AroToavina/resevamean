# Gestionnaire de Réservation Hôtelière - Aperçu du Projet

Une application Django full-stack complète pour la gestion des réservations d'hôtel, des chambres, des clients et des paiements.

## 🛠 Pile Technique
- **Backend :** Django (Python)
- **Base de données :** SQLite (développement par défaut)
- **Frontend :** Django Template Language (DTL)
- **Localisation :** Français (`fr-fr`), Fuseau horaire : `Africa/Nouakchott`

## 🏗 Structure du Projet
Le projet est organisé en plusieurs applications Django :
- `hotel` : Gestion des entités hôtelières.
- `chambre` : Types de chambres, équipements et gestion de l'état des chambres.
- `reservation` : Logique centrale de réservation, suivi des statuts et historique.
- `paiement` : Traitement des paiements (inclut le support pour Bankily).
- `client` : Profils clients et historique.
- `users` : Modèle utilisateur personnalisé (`User`) avec rôles : `admin`, `manager`, `receptionniste`, `gestion_chambre`.
- `services` : Services hôteliers supplémentaires (ex: petit-déjeuner, blanchisserie).
- `ville` : Gestion des villes/lieux.
- `templates` : Gabarits DTL globaux et spécifiques aux applications.
- `media` : Fichiers téléchargés (ex: images d'hôtels).

## 🚀 Commandes Clés

### Développement
- **Lancer le serveur :** `python manage.py runserver`
- **Appliquer les migrations :** `python manage.py migrate`
- **Créer des migrations :** `python manage.py makemigrations`
- **Créer un super-utilisateur :** `python manage.py createsuperuser`
- **Collecter les fichiers statiques :** `python manage.py collectstatic`

### Tests
- **Lancer les tests :** `python manage.py test` (Note : s'assurer que les tests sont implémentés dans les fichiers `tests.py` de chaque application)

## 🔑 Conventions de Développement
- **Rôles Utilisateurs :** Le système utilise un modèle utilisateur personnalisé `users.User`. Les permissions sont souvent vérifiées via le champ `role`.
- **Statut de Réservation :** Les réservations suivent un cycle de vie spécifique : `en_attente` -> `confirmee` -> `checkin` -> `checkout` ou `annulee`.
- **Media/Static :** Dans la configuration actuelle (`DEBUG = False`), les fichiers statiques et médias sont servis via `django.views.static.serve` dans `urls.py`. Pour la production, utiliser un serveur web dédié (Nginx/Apache).
- **Authentification :** La connexion du personnel se fait sur `/staff/login/`. Les clients ont leur propre interface sous `/client/`.

## 📝 TODOs & Observations
- Aucun fichier `requirements.txt` n'a été trouvé à la racine ; les dépendances devraient être documentées.
- Le projet est configuré avec `DEBUG = False` dans `settings.py`, ce qui est inhabituel pour un environnement de développement.
- La clé secrète (`SECRET_KEY`) est codée en dur ; utiliser des variables d'environnement pour la production.
