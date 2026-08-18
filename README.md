# BTP Manager — V1

Application de gestion de projets BTP avec le workflow **Survey → Devis → Achat → Chantier → Rapport de clôture**.

## Fonctionnalités de la V1

- Authentification Django et rôles prêts à attribuer : Administrateur, Direction, Conducteur de travaux, Métreur, Achats, Finance, Client.
- Répertoire clients et création de projets avec référence, budget, échéance et responsable.
- Workflow contrôlé : un Survey validé est requis pour le devis ; un devis validé pour les achats ; un achat reçu pour le chantier ; un chantier terminé pour le rapport final.
- Tableau de bord et suivi détaillé de chaque projet.
- Administration Django disponible sur `/admin/`.

## Prérequis

- Python 3.11 ou plus récent
- Node.js 20 ou plus récent
- PostgreSQL 15 ou plus récent

## Installation

1. Créez la base et l’utilisateur PostgreSQL :

```sql
CREATE USER btp_user WITH PASSWORD 'btp_password';
CREATE DATABASE btp_manager OWNER btp_user;
```

2. Copiez `.env.example` vers `.env`, puis adaptez les valeurs PostgreSQL et la clé secrète.

3. Installez le backend :

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py makemigrations business
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
```

4. Installez et construisez l’interface :

```bash
npm install
npm run build
```

Pour servir les fichiers compilés, passez `DJANGO_DEBUG=False` dans `.env` avant le déploiement et lancez aussi `python manage.py collectstatic`.

## Lancement

Dans un premier terminal :

```bash
.venv\\Scripts\\activate
python manage.py runserver
```

Dans un second terminal, uniquement pendant le développement de l’interface :

```bash
npm run dev
```

Ouvrez ensuite `http://127.0.0.1:8000/`.

## Évolutions recommandées

- Permissions fines par rôle et validation à deux niveaux pour les devis.
- Lignes de devis, catalogue articles, fournisseurs et pièces jointes.
- Planning, tâches chantier, coûts réels et marges.
- Génération PDF du devis et du rapport de clôture.
- API mobile et notifications.
