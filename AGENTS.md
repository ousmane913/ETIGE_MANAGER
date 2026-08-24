# Guide pour les agents

## Vue d’ensemble

- Application de gestion de projets BTP en Django 5.1–5.2, PostgreSQL, React 18, Inertia.js, Vite et Tailwind.
- Le backend Django possède les règles métier, l’authentification, les formulaires et les transitions du workflow.
- Le frontend React rend les pages Inertia et soumet les formulaires avec `useForm`.
- Le flux métier est : `Survey valide -> devis approuve -> achat recu -> chantier termine -> rapport de cloture`.

## Commandes

Consulter [README.md](README.md) pour l’installation complète et les variables d’environnement.

- Vérifier le backend : `python manage.py check`
- Appliquer les migrations : `python manage.py migrate`
- Initialiser les rôles : `python manage.py setup_roles`
- Lancer Django : `python manage.py runserver`
- Installer le frontend : `npm install`
- Construire le frontend : `npm run build`
- Lancer Vite en développement : `npm run dev`
- Tester Django : `python manage.py test`

PostgreSQL doit être disponible avant `migrate` ou `runserver`. En développement, Django utilise le port `8000` et Vite le port `5173`.

## Architecture à respecter

- `business/models.py` : modèles et invariants métier ; conserver les validations dans `clean()`.
- `business/forms.py` : `ModelForm` et présentation des champs.
- `business/views.py` : orchestration HTTP, transitions de statut et props envoyées à Inertia.
- `core/views.py` : authentification et tableau de bord.
- `core/middleware.py` : conversion des corps JSON en données de formulaire Django.
- `frontend/src/main.tsx` : bootstrap Inertia et résolution des pages.
- `frontend/src/pages/` : pages React ; `frontend/src/layouts/AppLayout.tsx` enveloppe les pages protégées.
- `templates/base.html` : layout Django/Inertia et chargement du bundle Vite.

Pour une modification du workflow, mettre à jour ensemble la règle du modèle, la transition de vue et l’affichage frontend concerné. Dans les vues, appeler `full_clean()` avant de sauvegarder les enregistrements métier. Préserver les migrations existantes et créer une nouvelle migration pour toute évolution de modèle.

## Conventions

- Python : noms métier en anglais, libellés utilisateur en français, décorateurs Django (`login_required`, `require_http_methods`) et `get_object_or_404`.
- Frontend : composants fonctionnels TypeScript, imports relatifs et classes Tailwind inline.
- Réutiliser les classes partagées de [frontend/src/styles.css](frontend/src/styles.css) : `.card`, `.btn`, `.btn-primary`, `.btn-muted`, `.input`.
- Les statuts backend sont des constantes en majuscules ; leur traduction d’interface est centralisée dans [frontend/src/components/Status.tsx](frontend/src/components/Status.tsx).
- Les URLs applicatives utilisent le français et un slash final.
- Après une modification backend, exécuter au minimum `python manage.py check`. Après une modification frontend, exécuter `npm run build`.

## Points de vigilance

- Ne jamais journaliser, afficher ou conserver des mots de passe, clés secrètes ou autres identifiants sensibles ; inspecter et corriger tout code de debug rencontré dans le chemin modifié.
- Ne pas contourner les transitions en changeant directement un statut depuis une nouvelle vue ou un composant.
- `Purchase` réutilise le dernier achat par défaut ; `?nouveau=1` force la création d’un achat séparé.
- `.env` est nécessaire pour une configuration réelle et ne doit pas être commité.
- En production, construire le frontend, définir `DJANGO_DEBUG=False`, puis lancer `python manage.py collectstatic`.
- Aucun linter, formateur ou test frontend n’est configuré ; ne pas inventer de commande qui n’existe pas.
