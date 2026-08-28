# 🚀 GUIDE DE DÉPLOIEMENT - MEROUNG AI

## 📱 Déployer sur Streamlit Cloud (Gratuit)

---

## ✅ ÉTAPE 1 : PRÉPARER GITHUB (5 min)

### 1.1 Créer un compte GitHub (si pas encore)
- Va sur https://github.com
- Click "Sign up"
- Complète le formulaire
- Vérifie ton email

### 1.2 Créer un nouveau repo

```
1. Sur GitHub, click "+" (top right)
2. New repository
3. Repository name : meroung-ai
4. Description : "Assistant pédagogique avec coaching"
5. Public (pour Streamlit Cloud)
6. Initialize with README ✓
7. Click "Create repository"
```

### 1.3 Cloner le repo localement

```bash
# Sur ton PC (terminal/PowerShell)
cd C:\Users\BOUYODA\PycharmProjects

# Cloner
git clone https://github.com/TON_USERNAME/meroung-ai.git

# Entrer dans le dossier
cd meroung-ai
```

---

## 📂 ÉTAPE 2 : PRÉPARER LES FICHIERS (2 min)

### 2.1 Copier les fichiers
```bash
# Copie depuis les outputs:
# - interface_ia.py
# - requirements.txt
# - .env.example
# - .gitignore

# Vers le dossier meroung-ai/

# Structure finale :
meroung-ai/
├── interface_ia.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
└── README.md
```

### 2.2 Créer le dossier .streamlit

```bash
# Si pas existe
mkdir .streamlit

# Copier config.toml dedans
# (ou créer avec ton éditeur)
```

### 2.3 Créer un README.md

```bash
# Dans le dossier racine, crée README.md :
```

```markdown
# Meroung AI 🤖

Assistant pédagogique personnel avec coaching authentique.

## Features

✨ **Meroung Academy** - Mode enseignant
- Élèves : apprentissage structuré
- Parents : support pédagogique
- Vision Gemini : analyse photos du travail
- Feedback authentique + encouragement

✨ **Meroung AI Général**
- Chat polyvalent
- Génération d'images
- Mode vocal
- Export PDF

## Tech

- **Frontend** : Streamlit
- **IA** : Google Gemini 3.6
- **Database** : SQLite
- **Images** : Pollinations.ai

## Déploiement

Déployé sur Streamlit Cloud.

```

---

## 🔐 ÉTAPE 3 : CONFIGURER SECRETS (2 min)

### 3.1 Sur Streamlit Cloud (IMPORTANT)

```
1. Va sur https://streamlit.io/cloud
2. Sign in avec GitHub
3. Attendez d'être connecté
4. Click "New app"
5. (on va faire ça après)
```

### 3.2 Ajouter la clé API (secrets)

Streamlit Cloud gère les secrets automatiquement :
- Ne JAMAIS commit la vraie clé dans .env
- Utiliser GitHub Secrets ou Streamlit Secrets

**Option A : Via Streamlit Dashboard**
```
1. Après deployment (étape 5)
2. Clique "Advanced settings"
3. Secrets
4. Ajoute :
   GEMINI_API_KEY=AIzaSyA...
   GEMINI_MODEL=gemini-3.6-flash
```

**Option B : .streamlit/secrets.toml (local)**
```toml
GEMINI_API_KEY = "AIzaSyA..."
GEMINI_MODEL = "gemini-3.6-flash"
```

---

## 📤 ÉTAPE 4 : PUSH SUR GITHUB (3 min)

```bash
# Dans le terminal, du dossier meroung-ai/

# 1. Ajouter tous les fichiers
git add .

# 2. Commit
git commit -m "Initial commit: Meroung AI v1.0"

# 3. Push vers GitHub
git push origin main

# ✅ Vérifie sur GitHub.com que les fichiers y sont
```

---

## 🌐 ÉTAPE 5 : DÉPLOYER SUR STREAMLIT CLOUD (2 min)

### 5.1 Aller sur Streamlit Cloud

```
https://streamlit.io/cloud
```

### 5.2 Sign in avec GitHub

```
1. Click "Sign in"
2. Authorize Streamlit
3. Select GitHub account
4. Authorize
```

### 5.3 Créer une nouvelle app

```
1. Click "New app"
2. Repository : ton_username/meroung-ai
3. Branch : main
4. Main file path : interface_ia.py
5. Click "Deploy"
```

### 5.4 Attendre le déploiement

```
Status : "Running" (1-2 minutes)
Tu vas voir :
- Build logs
- Python dependencies install
- App starting...
```

### 5.5 Ajouter les Secrets

```
1. App running ✓
2. Click menu (☰) en haut à droite
3. "Settings"
4. "Secrets"
5. Ajouter :

GEMINI_API_KEY=AIzaSyA...
GEMINI_MODEL=gemini-3.6-flash
APP_NAME=Meroung AI
```

### 5.6 App Redémarre Automatiquement

```
1-2 minutes
Puis : 🎉 APP LIVE !
```

---

## 🎉 RÉSULTAT

Après déploiement, tu auras :

```
🌐 URL : https://meroung-ai.streamlit.app
📱 Fonctionne sur :
   ✅ Desktop
   ✅ Tablet
   ✅ Mobile Android
   ✅ Mobile iOS

🔒 Sécurisé HTTPS
⚡ Rapide (global CDN)
🆓 Gratuit (tier Community)
```

---

## 📱 TESTER SUR MOBILE

```
1. Ouvre navigateur mobile
2. Va sur : https://meroung-ai.streamlit.app
3. Se connecter avec Google
4. Teste Meroung Academy
5. Upload une photo
6. Vérifie que tout fonctionne
```

---

## 🔄 MISES À JOUR FUTURES

Une fois déployé, pour chaque changement :

```bash
# 1. Code change localement
# 2. Test sur localhost:8501
# 3. Commit + Push

git add .
git commit -m "Feature: ajoute X"
git push origin main

# 4. Streamlit Cloud détecte auto et redéploie
# 5. App update en 1-2 min ! ✨
```

---

## ⚠️ TROUBLESHOOTING

### App ne démarre pas ?
```
1. Regarde les logs (Streamlit Dashboard)
2. Vérifie requirements.txt
3. Vérifie Python version (3.8+)
4. Redeploy : click "Reboot app"
```

### "Module not found" ?
```
1. requirements.txt manque une dépendance
2. Ajoute-la et push
3. Redeploy auto
```

### "API key invalid" ?
```
1. Vérifie GEMINI_API_KEY dans Secrets
2. Vérifie que c'est la bonne clé
3. Redeploy
```

### Mobile ne fonctionne pas ?
```
1. Ouvre DevTools (F12)
2. Regarde console pour errors
3. Teste sur desktop d'abord
4. C'est un problème navigateur mobile
```

---

## 📊 LIMITES STREAMLIT CLOUD GRATUIT

```
✅ 1 app par repository
✅ Resources suffisantes (usage normal)
✅ Sleep après 1h inactivité (reload auto)
✅ Pas de limitation temps d'execution
✅ Storage 1 GB per repo

⚠️ Si > 1 concurrent : ralentit
⚠️ Si > 100 utilisateurs/jour : penser upgrade
```

---

## 🚀 PROCHAINES ÉTAPES

Après deployment :

```
1. ✅ Partage l'URL avec des utilisateurs
2. ✅ Collecte feedback
3. ✅ Corrige bugs
4. ✅ Ajoute features
5. ✅ Itère rapidement en production
6. (Plus tard) Pense upgrade si besoin
```

---

## 📞 BESOIN D'AIDE ?

Streamlit Docs : https://docs.streamlit.io/
Forum : https://discuss.streamlit.io/
Status : https://status.streamlit.io/

---

**Voilà ! Tu es prêt ! 🚀**

Des questions avant de déployer ?
