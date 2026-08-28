# 🤖 Meroung AI - Assistant Pédagogique Personnel

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://meroung-ai.streamlit.app)

Assistant IA bienveillant et efficace avec **coaching pédagogique authentique**.

---

## ✨ Features

### 🎓 **Meroung Academy** - Mode Enseignant

**Pour ÉLÈVE :**
- 📖 Cours structuré et progressif
- 📝 Exercices sans correction immédiate
- 🔍 Vision Gemini analyse photos du travail
- 👏 Feedback authentique (efforts + corrections + encouragement)
- 💪 Motivation et progression

**Pour PARENT :**
- 👨‍🏫 Guide pédagogique pour aider l'enfant
- 📊 Exercices adaptés au niveau
- 💬 Conseils de communication
- ✅ Correction détaillée et feedback
- 🆘 Support continu de l'apprentissage

### 💬 **Meroung AI** - Mode Assistant Général

- 🎨 Chat polyvalent et adaptatif
- 🖼️ Génération d'images (Pollinations.ai)
- 🎤 Mode vocal avec transcription auto
- 📄 Export PDF des réponses
- 🌍 Multilingue FR/EN
- 📱 Responsive design (mobile, tablet, desktop)

---

## 🚀 Déploiement Rapide

### Option 1 : Streamlit Cloud (⭐ Recommandé - Gratuit)

```bash
# 1. Créer un compte GitHub : https://github.com
# 2. Créer repo "meroung-ai"
# 3. Pusher le code :

git add .
git commit -m "Initial commit: Meroung AI"
git push origin main

# 4. Aller sur https://streamlit.io/cloud
# 5. "New app" et sélectionner le repo
# 6. Ajouter secrets (Settings > Secrets) :
#    GEMINI_API_KEY=your_key_here
# 7. Deploy! ✅
```

**Résultat :** `https://meroung-ai.streamlit.app`

### Lire le guide détaillé :
👉 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 🛠️ Installation Locale

### Prérequis
- Python 3.8+
- Clé API Google Gemini (gratuite)

### Setup

```bash
# 1. Cloner le repo
git clone https://github.com/USERNAME/meroung-ai.git
cd meroung-ai

# 2. Créer .env
cp .env.example .env
# Éditer .env et ajouter ta clé API Gemini

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Lancer l'app
streamlit run interface_ia.py
```

**Accès :** `http://localhost:8501`

---

## 🔑 Configuration

### Clé API Gemini

1. Va sur https://aistudio.google.com/app/apikeys
2. "Create API Key"
3. Copie la clé
4. Ajoute dans `.env` :
   ```
   GEMINI_API_KEY=AIzaSyA...
   ```

### Variables d'Environnement

```env
# Obligatoire
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.6-flash

# Optionnel (defaults okay)
APP_NAME=Meroung AI
MAX_INPUT_LENGTH=30000
MAX_FILE_SIZE_MB=50
```

---

## 📱 Compatibilité

✅ **Desktop** (Windows, Mac, Linux)
✅ **Tablet** (iPad, Samsung Tab, etc.)
✅ **Mobile** (Android 6.0+, iOS 12.0+)

Responsive design automatique.

---

## 🏗️ Structure du Projet

```
meroung-ai/
├── interface_ia.py           # App principale (1100+ lignes)
├── requirements.txt          # Dépendances Python
├── .env.example             # Template variables
├── .gitignore               # Git config
├── .streamlit/
│   └── config.toml          # Streamlit config
├── DEPLOYMENT_GUIDE.md      # Guide détaillé
└── README.md                # Ce fichier
```

---

## 🎓 Utilisation Meroung Academy

### Workflow Élève

```
1. Sidebar → "🎓 Lancer Meroung Academy"
2. Choisir "👨‍🎓 Je suis élève"
3. Remplir nom + niveau d'étude
4. Demander aide (ex: "Explique les fractions")
5. Prof donne exercice + "À toi de jouer !"
6. Faire exercice sur papier
7. Prendre PHOTO de ton travail
8. Upload la photo
9. Meroung analyse + feedback authentique
   ├─ 👏 Reconnaît tes efforts
   ├─ ⚠️ Explique les erreurs
   ├─ ✅ Donne la correction
   └─ 💪 T'encourage
```

### Workflow Parent

```
1. Sidebar → "🎓 Lancer Meroung Academy"
2. Choisir "👨‍👩‍👧 Je suis parent d'élève"
3. Remplir infos (nom, enfant, classe)
4. Demander exercice (ex: "Exo maths 3ème")
5. Meroung propose exercice
6. Donner exercice à l'enfant
7. Enfant le fait sur papier
8. Prendre PHOTO
9. Upload la photo
10. Meroung analyse + feedback parent
    ├─ 👏 Valorise travail enfant
    ├─ ⚠️ Erreurs identifiées
    ├─ ✅ Correction complète
    └─ 💡 Conseils pour aider l'enfant
```

---

## 🔧 API & Dépendances

| Technologie | Version | Usage |
|-------------|---------|-------|
| Streamlit | 1.28.1 | Interface web |
| Google Gemini | 0.5.2 | IA principale |
| Pillow | 10.1.0 | Traitement images |
| fpdf2 | 2.7.1 | Export PDF |
| python-dotenv | 1.0.0 | Config env |

---

## 🔒 Sécurité

- ✅ Authentification Google OAuth
- ✅ Secrets gérés (pas de clés en clair)
- ✅ HTTPS automatique (Streamlit Cloud)
- ✅ Données utilisateur isolées
- ✅ Sessions sécurisées

---

## 📊 Limites Streamlit Cloud (Gratuit)

```
✅ Ressources suffisantes pour usage normal
✅ HTTPS automatique
✅ Mises à jour auto (git push)
✅ 1 GB storage par app

⚠️ Sleep après 1h inactivité (reload auto)
⚠️ Performance dégradée > 1 utilisateur concurrent
⚠️ Upgrade si > 100 utilisateurs actifs
```

---

## 🐛 Troubleshooting

### App ne démarre pas ?
```
→ Vérifier les logs sur Streamlit Dashboard
→ Vérifier requirements.txt est complet
→ Redeploy via dashboard
```

### "API Key invalid" ?
```
→ Vérifier clé dans Secrets (pas .env production)
→ Vérifier format : AIzaSyA...
→ Tester clé : https://aistudio.google.com
```

### Mobile ne fonctionne pas ?
```
→ Tester sur desktop d'abord
→ Vérifier navigateur à jour
→ Ouvrir console (F12) pour errors
```

### Photos ne s'uploadent pas ?
```
→ Vérifier taille < 50 MB
→ Vérifier format : JPG, PNG
→ Vérifier internet connection
```

---

## 🚀 Roadmap

- [x] Chat IA principal
- [x] Meroung Academy (élève + parent)
- [x] Vision Gemini (analyse photos)
- [x] Mode vocal
- [x] Export PDF
- [x] Mobile responsive
- [ ] App native Android/iOS (future)
- [ ] Intégration vidéo (future)
- [ ] Analytics (future)
- [ ] Badges de progression (future)

---

## 👨‍💼 À Propos

**Créateur :** Bouyamoung Meroung  
**Entreprise :** Meroung Tech (Yaoundé, Cameroun)  
**Tech Stack :** Python + Streamlit + Gemini AI

---

## 📄 Licence

MIT License - Libre d'utilisation

---

## 📞 Support

- 📧 Contact : ephrahimbouyoda@gmail.com
- 🐛 Issues : GitHub Issues
- 💬 Feedback : Bienvenu !

---

## 🎉 Merci !

Merci d'utiliser Meroung AI !  
Ton feedback aide à améliorer l'app.

**Garde le sourire en apprenant ! 🌟**
