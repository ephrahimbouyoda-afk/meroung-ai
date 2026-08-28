# ⚡ QUICK START - 10 MINUTES POUR DÉPLOYER

## 📋 Prérequis

- ✅ Compte GitHub (créer sur https://github.com)
- ✅ Clé API Gemini (créer sur https://aistudio.google.com/app/apikeys)
- ✅ Git installé sur ton PC

---

## 🚀 DÉPLOIEMENT EN 5 ÉTAPES

### ÉTAPE 1️⃣ : Créer Repo GitHub (2 min)

```
1. Va sur https://github.com
2. Sign in ou Create account
3. Clique "+" → "New repository"
4. Name: meroung-ai
5. Public ✓
6. "Create repository"
```

### ÉTAPE 2️⃣ : Cloner & Préparer (2 min)

```bash
# Terminal / PowerShell
cd C:\Users\BOUYODA\PycharmProjects

# Clone
git clone https://github.com/TON_USERNAME/meroung-ai.git
cd meroung-ai

# Copier les fichiers depuis outputs/
# interface_ia.py
# requirements.txt
# .env.example
# .gitignore
# .streamlit/config.toml
# README.md
# DEPLOYMENT_GUIDE.md
```

### ÉTAPE 3️⃣ : Push sur GitHub (2 min)

```bash
git add .
git commit -m "Initial: Meroung AI v1.0"
git push origin main
```

✅ Vérifie sur GitHub.com que les fichiers y sont

### ÉTAPE 4️⃣ : Déployer sur Streamlit Cloud (2 min)

```
1. Va sur https://streamlit.io/cloud
2. Sign in avec GitHub
3. Authorize Streamlit
4. "New app"
5. Repository: TON_USERNAME/meroung-ai
6. Branch: main
7. Main file: interface_ia.py
8. Click "Deploy"
9. Attends 1-2 minutes (Status: Running)
```

### ÉTAPE 5️⃣ : Configurer Secrets (1 min)

```
1. App running ✓
2. Menu (☰) → Settings
3. Secrets
4. Copie-colle :

GEMINI_API_KEY=AIzaSyA...
GEMINI_MODEL=gemini-3.6-flash
APP_NAME=Meroung AI
```

App redémarre auto → 🎉 LIVE !

---

## 🌐 RÉSULTAT

```
🎉 URL : https://meroung-ai.streamlit.app
📱 Fonctionne : Desktop + Mobile + Tablet
✅ Sécurisé HTTPS
🆓 Gratuit
```

---

## 📱 TESTER

```
1. Mobile : ouvre https://meroung-ai.streamlit.app
2. Se connecter Google
3. "🎓 Lancer Meroung Academy"
4. Test élève/parent
5. Upload une photo
6. Vérifie que tout marche !
```

---

## 🔄 MISES À JOUR APRÈS (Très simple!)

```bash
# À chaque changement :
git add .
git commit -m "Feature: ajoute X"
git push origin main

# Streamlit redéploie auto en 1-2 min ✨
```

---

## ⚠️ AIDE RAPIDE

| Problème | Solution |
|----------|----------|
| "Module not found" | Ajouter dans requirements.txt + push |
| "API key invalid" | Vérifier Secrets (pas .env) |
| App très lente | Redeploy (Reboot app button) |
| Mobile ne marche pas | Tester desktop d'abord |

---

## 🎯 C'EST TOUT !

**10 minutes et c'est live ! 🚀**

Des questions ? Lire DEPLOYMENT_GUIDE.md
