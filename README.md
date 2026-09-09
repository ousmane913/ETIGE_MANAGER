# BTP Manager — V1

Application de gestion de projets BTP avec le workflow **Survey → Devis → Achat → Chantier → Rapport de clôture**.

Pour le déploiement cloud avec domaine, HTTPS, sauvegardes et accès depuis le domicile, consulter [DEPLOIEMENT_PRODUCTION.md](DEPLOIEMENT_PRODUCTION.md).

## Fonctionnalités de la V1

- Authentification Django et rôles : **Employé**, **Manager**, **DT** (direction technique) et **DG** (direction générale). Le super-utilisateur a les mêmes droits que le DG.
- Répertoire clients : chaque projet est lié à une fiche client (nom, email, téléphone). L’email du client sert à l’envoi du devis.
- Création de projets avec numéro ETIGE automatique (`PRJ-001`, …), référence, budget, échéance et responsable.
- Workflow contrôlé : le survey est optionnel ; s’il existe, il doit être validé avant le devis. Un devis non refusé est requis pour les achats ; un achat reçu pour le chantier ; un chantier terminé pour le rapport de clôture.
- Droits : l’employé saisit ; le DT voit les montants et suit le chantier ; seul le DG peut modifier ou supprimer un projet, et supprimer un client.
- Tableau de bord, planning, PDF devis / planning, envoi du devis par email.
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

- Versions de devis / avenants (plusieurs devis par projet).
- Lignes d’achat, catalogue articles, fournisseurs et pièces jointes.
- Suivi devis vs achats vs dépenses (marge par chantier).
- Validation à deux niveaux pour les devis.
- API mobile et notifications.
