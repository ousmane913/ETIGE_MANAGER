# Guide de déploiement sur Railway.app

## 🚀 Pourquoi Railway.app ?

- **Gratuit** avec $5 de crédit mensuel (suffisant pour usage personnel)
- **Pas de dormance** contrairement à Render
- **Performance supérieure** aux alternatives gratuites
- **URL automatique** : `votre-app.up.railway.app`
- **Base de données PostgreSQL** incluse
- **Déploiement automatique** via Git

## 📋 Étapes de déploiement

### 1. Préparation du projet

Les fichiers suivants ont été créés automatiquement :
- `railway.json` - Configuration Railway
- `Procfile` - Commandes de démarrage
- `nixpacks.toml` - Configuration de construction
- `.env.example` - Variables d'environnement exemple

### 2. Création du compte Railway

1. Allez sur [railway.app](https://railway.app)
2. Créez un compte avec GitHub/GitLab
3. Vérifiez votre email

### 3. Création du nouveau projet

1. Cliquez sur "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Autorisez Railway à accéder à votre repository
4. Sélectionnez votre repository `ETIGE-manager`

### 4. Configuration des services

#### Service Web (Django)
Railway détectera automatiquement que c'est une application Python.

**Variables d'environnement à configurer :**

Dans votre projet Railway, allez dans "Settings" → "Variables" et ajoutez :

```
DJANGO_SECRET_KEY=clé_aleatoire_ici
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.railway.app,.up.railway.app,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app,http://localhost:8000
```

Pour générer une clé secrète :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Base de données PostgreSQL

1. Dans votre projet Railway, cliquez sur "New Service"
2. Sélectionnez "Database" → "PostgreSQL"
3. Railway créera automatiquement la base de données

**Variable DATABASE_URL sera automatiquement configurée par Railway.**

### 5. Configuration du frontend

Le frontend sera construit automatiquement grâce au script `postinstall` dans `package.json`.

### 6. Commandes de déploiement initial

Le premier déploiement peut prendre 5-10 minutes :
- Installation des dépendances Python
- Installation des dépendances Node.js
- Construction du frontend Vite
- Exécution des migrations Django
- Collecte des fichiers statiques

### 7. Accès à l'application

Une fois le déploiement terminé :
1. Cliquez sur votre service web
2. Cliquez sur "Generate Domain" si nécessaire
3. Votre URL sera : `https://votre-projet.up.railway.app`

## 🔧 Configuration avancée

### Commandes de construction personnalisées

Si vous avez besoin de modifier la construction :
1. Allez dans "Settings" → "Build"
2. Modifiez les commandes selon vos besoins

### Gestion des fichiers statiques

En production, les fichiers statiques sont servis par Django :
- Les fichiers sont collectés dans `staticfiles/`
- Servis via `STATIC_URL = 'static/'`

### Sauvegarde de la base de données

Railway propose des sauvegardes automatiques pour PostgreSQL :
- Allez dans votre service PostgreSQL
- "Backups" → "Create Backup"

## 📊 Monitoring

### Logs

1. Cliquez sur votre service web
2. "Logs" pour voir les logs en temps réel
3. "Metrics" pour les performances

### Déploiements

1. "Deployments" pour voir l'historique
2. Chaque push Git = nouveau déploiement automatique

## 🔄 Mises à jour

Pour mettre à jour votre application :
1. Faites les modifications localement
2. Commit et push sur GitHub
3. Railway déploie automatiquement

```bash
git add .
git commit -m "Description des modifications"
git push origin main
```

## 🐛 Dépannage

### Erreur de migration

Si les migrations échouent :
1. Allez dans "Settings" → "Variables"
2. Ajoutez `RUN_MIGRATIONS=false`
3. Redéployez
4. Exécutez manuellement les migrations via Railway Console

### Problèmes de frontend

Si le frontend ne se construit pas :
1. Vérifiez que `package.json` contient le script `postinstall`
2. Vérifiez les logs de construction
3. Assurez-vous que tous les fichiers frontend sont présents

### Erreur de base de données

Si la connexion échoue :
1. Vérifiez que `DATABASE_URL` est bien configurée
2. Vérifiez que le service PostgreSQL est démarré
3. Regardez les logs pour les erreurs de connexion

## 💰 Coûts

- **Gratuit** : $5 de crédit mensuel
- **Usage personnel** : Généralement suffisant
- **Dépassement** : Railway vous avertit avant

## 🔒 Sécurité

- Clé secrète générée aléatoirement
- HTTPS automatique
- Variables d'environnement sécurisées
- Base de données privée

## 📞 Support

- Documentation : [docs.railway.app](https://docs.railway.app)
- Support : [support.railway.app](https://support.railway.app)
- Communauté : Discord Railway

## 🎉 Avantages finaux

Une fois déployé :
- ✅ Plus besoin de `venv` ou `npm run dev`
- ✅ Lien permanent accessible partout
- ✅ Mises à jour automatiques
- ✅ Monitoring intégré
- ✅ Sauvegardes automatiques
- ✅ HTTPS gratuit
