import datetime
import json
import os
import re
import sqlite3
import logging
import sys
import time
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from fpdf import FPDF
import database

# --- CHARGEMENT VARIABLES D'ENVIRONNEMENT ---
load_dotenv()

# --- CONFIGURATION LOGGING ---
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file_streamlit = os.getenv("LOG_FILE_STREAMLIT", "interface_ia.log")

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s",
    handlers=[
        logging.FileHandler(log_file_streamlit),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION CONSTANTES ---
APP_NAME = os.getenv("APP_NAME", "Meroung AI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 30000))
DISCUSSIONS_FOLDER = os.getenv("DISCUSSIONS_FOLDER", "discussions")
DATABASE_NAME = os.getenv("DATABASE_NAME", "meroung_ai.db")
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
RATE_LIMIT_WAIT = int(os.getenv("RATE_LIMIT_WAIT", 60))

# --- VALIDATION CONFIGURATION ---
if not GEMINI_API_KEY:
    logger.critical("❌ GEMINI_API_KEY non trouvée")
    st.error("❌ Clé API Gemini introuvable. Crée un fichier `.env` avec `GEMINI_API_KEY=ta_clé`")
    st.stop()

# --- INITIALISATION GEMINI ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info(f"✅ Gemini API configurée")
except Exception as e:
    logger.critical(f"❌ Erreur configuration Gemini : {e}")
    st.error("❌ Impossible de configurer Gemini API")
    st.stop()

# --- CRÉATION DOSSIER DISCUSSIONS ---
if not os.path.exists(DISCUSSIONS_FOLDER):
    os.makedirs(DISCUSSIONS_FOLDER)
    logger.info(f"📁 Dossier créé : {DISCUSSIONS_FOLDER}")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# --- STYLE CSS ---
st.markdown("""
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }

    [data-testid="stChatMessage"] {
        padding: 0.5rem 1rem;
        line-height: 1.6;
        font-size: 15px;
    }

    .stChatInput textarea {
        font-size: 14px;
        line-height: 1.5;
    }

    .academy-welcome {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 60px 40px;
        border-radius: 12px;
        text-align: center;
        margin: 40px 0;
    }

    .academy-welcome h1 {
        font-size: 36px;
        margin-bottom: 10px;
    }

    .academy-welcome p {
        font-size: 18px;
        margin-bottom: 30px;
        opacity: 0.95;
    }

    .academy-info {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
        font-size: 13px;
        color: #333;
    }

    .exercise-box {
        background: #fffbf0;
        border-left: 4px solid #ff9800;
        padding: 16px;
        border-radius: 4px;
        margin: 16px 0;
    }

    .correction-box {
        background: #f0f8f4;
        border-left: 4px solid #4caf50;
        padding: 16px;
        border-radius: 4px;
        margin: 16px 0;
    }

    .effort-recognition {
        background: #fce4ec;
        border-left: 4px solid #e91e63;
        padding: 16px;
        border-radius: 4px;
        margin: 16px 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if "horodatages_requetes" not in st.session_state:
    st.session_state.horodatages_requetes = []
if "nb_requetes_session" not in st.session_state:
    st.session_state.nb_requetes_session = 0
if "prochaine_reponse_vocale" not in st.session_state:
    st.session_state.prochaine_reponse_vocale = False
if "dernier_audio_traite" not in st.session_state:
    st.session_state.dernier_audio_traite = None
if "mode_app" not in st.session_state:
    st.session_state.mode_app = "general"
if "academy_context" not in st.session_state:
    st.session_state.academy_context = None
if "exercice_donne" not in st.session_state:
    st.session_state.exercice_donne = False


# --- FONCTIONS UTILITAIRES ---
def slug_utilisateur(identifiant: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", identifiant.lower()).strip("_") or "utilisateur"


def dossier_utilisateur(identifiant: str) -> str:
    dossier = os.path.join(DISCUSSIONS_FOLDER, slug_utilisateur(identifiant))
    os.makedirs(dossier, exist_ok=True)
    return dossier


def nom_fichier_horodate(dossier=None):
    dossier = dossier or st.session_state.get("dossier_discussions", DISCUSSIONS_FOLDER)
    return f"{dossier}/chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def chemin_profil_utilisateur(identifiant: str) -> str:
    return os.path.join(dossier_utilisateur(identifiant), "_profil.json")


def charger_profil_utilisateur(identifiant: str) -> dict:
    chemin = chemin_profil_utilisateur(identifiant)
    defaut = {
        "persona": "",
        "memoire": "",
        "modele": GEMINI_MODEL,
        "langue_preference": "auto"
    }
    if os.path.exists(chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                profil = json.load(f)
                defaut.update(profil)
        except Exception as e:
            logger.warning(f"⚠️ Erreur lecture profil : {e}")
    return defaut


def sauvegarder_profil_utilisateur(identifiant: str, profil: dict):
    chemin = chemin_profil_utilisateur(identifiant)
    try:
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(profil, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Profil sauvegardé")
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde profil : {e}")


def sauvegarder_discussion():
    try:
        with open(st.session_state.fichier_courant, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde : {e}")


def detecter_langue(texte: str) -> str:
    if not texte:
        return "auto"
    if re.search(r"[àâäéèêëïîôöùûüçœæ]", texte.lower()):
        return "FR"
    if re.search(r"\b(bonjour|salut|oui|non|merci|s'il vous plaît)\b", texte.lower()):
        return "FR"
    if re.search(r"\b(hello|hi|yes|no|thank|please)\b", texte.lower()):
        return "EN"
    return "EN" if len(re.findall(r"[a-z]{3,}", texte.lower()[:50])) > 0 else "FR"


MOTS_CLES_IMAGE = [
    r"cr[ée]e?r?\s+(?:une?\s+)?(?:image|photo|illustration|dessin)",
    r"g[ée]n[èe]re?r?\s+(?:une?\s+)?(?:image|photo|illustration|dessin)",
    r"donnes?[\s-]?moi\s+une?\s+(?:image|photo)",
    r"fais[\s-]?moi\s+une?\s+(?:image|photo|illustration|dessin)",
]
MOTS_EXCLUSION = ["fonction", "code", "script", "programme", "résumé", "tableau", "texte"]


def est_une_demande_image(texte):
    texte_l = texte.lower()
    if any(mot in texte_l for mot in MOTS_EXCLUSION):
        return False
    return any(re.search(motif, texte_l) for motif in MOTS_CLES_IMAGE)


def extraire_sujet_image(prompt_original):
    sujet = prompt_original.lower()
    formules_a_retirer = [
        r"cr[ée]e?r?\s+(?:moi\s+)?(?:une?\s+)?(?:image|photo|illustration|dessin)\s*(?:de|d')?",
        r"g[ée]n[èe]re?r?\s+(?:moi\s+)?(?:une?\s+)?(?:image|photo|illustration|dessin)\s*(?:de|d')?",
    ]
    for motif in formules_a_retirer:
        sujet = re.sub(motif, "", sujet)
    return sujet.strip(" .,?!'-") or prompt_original


def construire_historique_sdk(messages):
    historique = []
    for m in messages[:-1]:
        texte = f"[Image générée : {m.get('text', '')}]" if m.get("type") == "image" else m.get("text", "")
        historique.append({"role": m["role"], "parts": [texte]})
    return historique


def _parser_blocs_texte_et_tableaux(texte: str):
    lignes = texte.splitlines()
    blocs = []
    paragraphe_courant = []
    i = 0

    def _est_ligne_tableau(l):
        l = l.strip()
        return l.startswith("|") and l.endswith("|") and l.count("|") >= 2

    def _est_separateur(l):
        l = l.strip().strip("|")
        cellules = [c.strip() for c in l.split("|")]
        return all(re.fullmatch(r":?-{2,}:?", c) for c in cellules if c != "")

    while i < len(lignes):
        ligne = lignes[i]
        if _est_ligne_tableau(ligne) and i + 1 < len(lignes) and _est_ligne_tableau(lignes[i + 1]) and _est_separateur(
                lignes[i + 1]):
            if paragraphe_courant:
                blocs.append({"type": "texte", "contenu": "\n".join(paragraphe_courant).strip()})
                paragraphe_courant = []
            lignes_tableau = []
            j = i
            while j < len(lignes) and _est_ligne_tableau(lignes[j]):
                if j != i + 1:
                    cellules = [c.strip() for c in lignes[j].strip().strip("|").split("|")]
                    lignes_tableau.append(cellules)
                j += 1
            blocs.append({"type": "tableau", "lignes": lignes_tableau})
            i = j
        else:
            paragraphe_courant.append(ligne)
            i += 1

    if paragraphe_courant:
        blocs.append({"type": "texte", "contenu": "\n".join(paragraphe_courant).strip()})
    return blocs


def generer_pdf_depuis_texte(titre: str, texte: str) -> bytes:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("courier", "B", 14)
    pdf.multi_cell(0, 10, titre)
    pdf.ln(2)

    pdf.set_font("courier", "", 11)
    for bloc in _parser_blocs_texte_et_tableaux(texte):
        if bloc["type"] == "texte":
            if bloc["contenu"]:
                contenu = re.sub(r"\*\*(.+?)\*\*", r"\1", bloc["contenu"])
                contenu = re.sub(r"`([^`]+)`", r"\1", contenu)
                contenu = contenu.replace("—", "-").replace("–", "-")
                pdf.set_font("courier", "", 11)
                pdf.multi_cell(0, 6, contenu)
                pdf.ln(3)
        elif bloc["type"] == "tableau" and bloc["lignes"]:
            pdf.set_font("courier", "", 10)
            try:
                with pdf.table() as table:
                    for rang, ligne_donnees in enumerate(bloc["lignes"]):
                        row = table.row()
                        for cellule in ligne_donnees:
                            cellule_nettoyee = cellule.replace("—", "-").replace("–", "-")
                            row.cell(cellule_nettoyee)
            except Exception as e:
                logger.warning(f"⚠️ Erreur rendu tableau PDF : {e}")
                pdf.set_font("courier", "", 11)
                for ligne_donnees in bloc["lignes"]:
                    contenu_ligne = " | ".join(ligne_donnees).replace("—", "-").replace("–", "-")
                    pdf.multi_cell(0, 6, contenu_ligne)
            pdf.ln(3)

    return bytes(pdf.output())


def lire_a_voix_haute(texte: str):
    texte_propre = re.sub(r"[`*_#>]", "", texte).replace("\n", " ").strip()
    if not texte_propre:
        return
    texte_js = json.dumps(texte_propre)
    langue_voix = "en-US" if detecter_langue(texte_propre) == "EN" else "fr-FR"
    st.components.v1.html(
        f"""
        <script>
            const texte = {texte_js};
            const utterance = new SpeechSynthesisUtterance(texte);
            utterance.lang = "{langue_voix}";
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0,
    )


def analyser_travail_eleve(image_bytes, context, prompt_utilisateur):
    """Analyse le travail de l'élève avec vision Gemini et réagit comme enseignant"""

    role_user = context.get("role")

    if role_user == "eleve":
        eleve_nom = context.get("nom", "Élève")
        eleve_niveau = context.get("niveau", "Lycée")

        system_instruction = (
            f"Tu es Meroung AI, un enseignant bienveillant et encourageant. "
            f"Élève : {eleve_nom} ({eleve_niveau})\n\n"
            f"Tu viens de recevoir une PHOTO du travail de {eleve_nom}.\n\n"
            f"TES RESPONSABILITÉS :\n"
            f"1. ANALYSER LE TRAVAIL : regarde attentivement ce qu'il a écrit/dessiné\n"
            f"2. RECONNAÎTRE LES EFFORTS : félicite les bonnes tentatives, valorise la démarche\n"
            f"3. IDENTIFIER LES ERREURS : explique clairement où c'est faux et pourquoi\n"
            f"4. DONNER LA CORRECTION : explique la bonne solution de façon progressive\n"
            f"5. ENCOURAGER : termine en motivant pour le prochain exercice\n\n"
            f"Structure ta réponse ainsi :\n"
            f"👏 EFFORTS & POINTS POSITIFS (ce qu'il a bien fait)\n"
            f"⚠️ CORRECTIONS (les erreurs et explications)\n"
            f"✅ SOLUTION COMPLÈTE (la bonne réponse expliquée)\n"
            f"💪 ENCOURAGEMENT (valorise et motive)\n"
        )
    else:  # parent
        enfant_nom = context.get("enfant_nom", "votre enfant")
        parent_nom = context.get("parent_nom", "parent")
        enfant_classe = context.get("enfant_classe", "sa classe")

        system_instruction = (
            f"Tu es Meroung AI, un assistant pédagogique pour parent. "
            f"Parent : {parent_nom}\n"
            f"Enfant : {enfant_nom} ({enfant_classe})\n\n"
            f"Tu viens de recevoir une PHOTO du travail de {enfant_nom}.\n\n"
            f"TES RESPONSABILITÉS :\n"
            f"1. ANALYSER LE TRAVAIL : évalue ce que l'enfant a fait\n"
            f"2. RECONNAÎTRE LES EFFORTS : aide le parent à valoriser le travail de l'enfant\n"
            f"3. IDENTIFIER LES ERREURS : explique clairement ce qui est faux\n"
            f"4. DONNER LA CORRECTION : montre la bonne solution\n"
            f"5. GUIDER LE PARENT : conseille comment aider l'enfant à progresser\n\n"
            f"Structure ta réponse ainsi :\n"
            f"👏 POINTS POSITIFS (valorise le travail)\n"
            f"⚠️ ERREURS (ce qui ne va pas)\n"
            f"✅ CORRECTION (la bonne solution)\n"
            f"💡 CONSEIL AU PARENT (comment aider l'enfant)\n"
        )

    generation_config = {"max_output_tokens": 2048}

    model = genai.GenerativeModel(
        model_name="models/gemini-3.6-flash",
        system_instruction=system_instruction,
        generation_config=generation_config,
    )

    try:
        contenu = [
            f"Voici le travail de l'élève sur cet exercice :\n\n{prompt_utilisateur}\n\nAnalyse la photo du travail :",
            {"mime_type": "image/jpeg", "data": image_bytes} if isinstance(image_bytes, bytes) else image_bytes
        ]

        response_stream = model.generate_content(contenu, stream=True)

        def _flux_texte():
            for morceau in response_stream:
                if morceau.text:
                    yield morceau.text

        return st.write_stream(_flux_texte)

    except Exception as e:
        logger.error(f"❌ Erreur analyse image : {e}")
        return None


def generer_et_ajouter_reponse(prompt_texte, contenu_requete):
    """Génère la réponse IA"""
    username = st.session_state.get("user_connecte")
    profil = st.session_state.get("profil_utilisateur", {})
    modele_choisi = profil.get("modele") or GEMINI_MODEL
    persona = (profil.get("persona") or "").strip()
    memoire = (profil.get("memoire") or "").strip()

    nom_actuel = st.session_state.get("user_connecte", "l'utilisateur")
    maintenant = datetime.datetime.now().strftime("%A %d/%m/%Y à %H:%M")

    langue_detectee = detecter_langue(prompt_texte)
    if langue_detectee == "EN":
        instruction_langue = (
            "You must respond ENTIRELY in English. "
            "If the user asks for a translation, provide the exact translation requested. "
            "Otherwise, never mix English and French in a single response."
        )
    else:
        instruction_langue = (
            "Tu dois répondre ENTIÈREMENT en français. "
            "Si l'utilisateur demande une traduction, fournis la traduction exacte demandée. "
            "Sinon, ne mélange jamais français et anglais dans une même réponse."
        )

    # --- SYSTÈME PROMPT SPÉCIAL POUR ACADEMY ---
    if st.session_state.mode_app == "academy" and st.session_state.academy_context:
        context = st.session_state.academy_context
        role_user = context.get("role")

        if role_user == "eleve":
            eleve_nom = context.get("nom", "Élève")
            eleve_niveau = context.get("niveau", "Lycée")
            system_instruction = (
                f"Tu es Meroung AI, un enseignant personnel bienveillant et efficace. "
                f"Tu enseignes au niveau {eleve_niveau}. "
                f"Élève : {eleve_nom}\n"
                f"{instruction_langue}\n\n"
                f"📚 TES RESPONSABILITÉS :\n"
                f"1. ENSEIGNER CLAIREMENT : explique progressivement et simplement\n"
                f"2. DONNER LES EXERCICES : fournir des exercices structurés SANS la correction immédiate\n"
                f"3. ANALYSER LE TRAVAIL : quand l'élève envoie une photo de son travail :\n"
                f"   - Féliciter les efforts fournis\n"
                f"   - Identifier les erreurs (si présentes)\n"
                f"   - Expliquer la bonne solution\n"
                f"   - Encourager la progression\n"
                f"4. ADAPTER AU NIVEAU {eleve_niveau}\n"
                f"\n"
                f"Quand tu donnes un exercice, termine avec :\n"
                f"'À toi de jouer ! Fais cet exercice sur ton cahier ou sur papier, "
                f"puis prends une PHOTO et envoie-la moi. Je vais analyser et te donner "
                f"mon feedback d'enseignant !'\n"
                f"Date/heure : {maintenant}"
            )
        else:  # parent
            enfant_nom = context.get("enfant_nom", "votre enfant")
            enfant_classe = context.get("enfant_classe", "sa classe")
            parent_nom = context.get("parent_nom", "parent")
            system_instruction = (
                f"Tu es Meroung AI, un assistant pédagogique pour parents. "
                f"Parent : {parent_nom}\n"
                f"Enfant : {enfant_nom} ({enfant_classe})\n"
                f"{instruction_langue}\n\n"
                f"👨‍🏫 TES RESPONSABILITÉS :\n"
                f"1. EXPLIQUER AU PARENT : aide-le à comprendre le sujet\n"
                f"2. DONNER UN EXERCICE : propose un exercice que le parent peut donner à l'enfant\n"
                f"3. ANALYSER LE TRAVAIL : quand le parent envoie la photo du travail de l'enfant :\n"
                f"   - Valoriser les efforts de l'enfant\n"
                f"   - Identifier les erreurs\n"
                f"   - Donner la bonne solution\n"
                f"   - Conseiller le parent sur comment aider l'enfant\n"
                f"4. ÊTRE RASSURANT ET CONSTRUCTIF\n"
                f"\n"
                f"Quand tu donnes un exercice, termine avec :\n"
                f"'Donne cet exercice à {enfant_nom}, puis demande-lui de faire le travail "
                f"sur son cahier. Prenez une PHOTO du travail et renvoyez-la moi. "
                f"Je vais analyser et donner mon feedback pédagogique !'\n"
                f"Date/heure : {maintenant}"
            )
    else:
        system_instruction = (
            f"Tu t'appelles {APP_NAME}. "
            f"Tu es une IA créée par Ephrahim Bouyoda pour l'entrepreneuriat africain. "
            f"Si on te demande qui t'a créé, dis : 'Je suis {APP_NAME}, créé par Ephrahim Bouyoda'. "
            f"Si on te demande seulement 'quel est ton nom', réponds UNIQUEMENT avec '{APP_NAME}'. "
            f"\n\n{instruction_langue}\n\n"
            f"Date/heure : {maintenant}. "
        )

    if persona:
        system_instruction += f"\n\nInstructions personnelles : {persona}"
    if memoire:
        system_instruction += f"\n\nMémoire utilisateur : {memoire}"

    generation_config = {"max_output_tokens": 8192}

    model = genai.GenerativeModel(
        model_name=modele_choisi,
        system_instruction=system_instruction,
        generation_config=generation_config,
    )

    with st.chat_message("assistant", avatar="🤖"):
        if est_une_demande_image(prompt_texte):
            logger.info("🖼️ Demande image détectée")
            sujet_image = extraire_sujet_image(prompt_texte)
            url_img = f"https://image.pollinations.ai/prompt/{sujet_image.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
            reponse_texte = f"Image générée : {prompt_texte}"
            st.image(url_img, caption=reponse_texte)
            st.session_state.messages.append({"role": "model", "text": reponse_texte, "type": "image", "url": url_img})
        else:
            for tentative in range(1, RETRY_ATTEMPTS + 1):
                try:
                    historique_sdk = construire_historique_sdk(st.session_state.messages)
                    chat_session = model.start_chat(history=historique_sdk)

                    response_stream = chat_session.send_message(contenu_requete, stream=True)

                    def _flux_texte():
                        for morceau in response_stream:
                            if morceau.text:
                                yield morceau.text

                    reponse_complete = st.write_stream(_flux_texte)
                    if reponse_complete:
                        st.session_state.messages.append({"role": "model", "text": reponse_complete})
                        if st.session_state.get("prochaine_reponse_vocale"):
                            lire_a_voix_haute(reponse_complete)
                            st.session_state.prochaine_reponse_vocale = False
                    break
                except Exception as e:
                    erreur_str = str(e)
                    logger.warning(f"⚠️ Erreur (tentative {tentative}/{RETRY_ATTEMPTS}) : {erreur_str[:100]}")

                    if "429" in erreur_str:
                        if tentative < RETRY_ATTEMPTS:
                            st.warning(f"⏳ Rate limit.")
                            time.sleep(RATE_LIMIT_WAIT)
                            continue
                        err_msg = "❌ Quota API dépassé."
                        st.error(err_msg)
                        st.session_state.messages.append({"role": "model", "text": err_msg})
                        break

                    elif "401" in erreur_str or "UNAUTHENTICATED" in erreur_str:
                        logger.critical("❌ Clé API invalide")
                        err_msg = "❌ Clé API invalide."
                        st.error(err_msg)
                        st.session_state.messages.append({"role": "model", "text": err_msg})
                        break

                    elif "403" in erreur_str:
                        logger.error("❌ Permission refusée")
                        err_msg = "❌ Accès refusé."
                        st.error(err_msg)
                        st.session_state.messages.append({"role": "model", "text": err_msg})
                        break

                    if tentative < RETRY_ATTEMPTS:
                        attente = RETRY_DELAY * tentative
                        st.info(f"⏳ Retry dans {attente}s...")
                        time.sleep(attente)
                        continue
                    err_msg = f"Erreur : {erreur_str[:100]}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "model", "text": err_msg})
                    break

        sauvegarder_discussion()
        return True


# ==========================================
# GESTION DE LA CONNEXION GOOGLE
# ==========================================
# ============================================================
# 🔐 AUTHENTIFICATION GOOGLE - MEROUNG AI
# ============================================================

# Vérifier si l'utilisateur est connecté
try:
    is_logged_in = st.user.is_logged_in
except Exception:
    is_logged_in = False


# ------------------------------------------------------------
# ÉCRAN DE CONNEXION
# ------------------------------------------------------------
if not is_logged_in:

    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
        [data-testid="stSidebarUserContent"] { display: none; }
        html, body { background: #fafafa; }

        /* Style du bouton pour qu'il ressemble au modèle épuré */
        .stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            border: none !important;
        }
        .stButton > button:hover {
            background-color: #222222 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Centrer la carte sur la page
    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        st.markdown(
            "<div style='text-align: center; font-size: 28px; font-weight: 600; margin-bottom: 30px; color: #111;'>Se connecter</div>",
            unsafe_allow_html=True)

        # La carte blanche aux bordures arrondies (similaire au modèle)
        with st.container(border=True):
            st.markdown(
                "<div style='text-align: center; font-weight: 700; font-size: 18px; color: #111; margin-top: 10px;'>🤖 Meroung AI</div>",
                unsafe_allow_html=True)
            st.markdown(
                "<div style='text-align: center; color: #666; font-size: 13px; margin-bottom: 25px;'>Personnel auxiliaire pédagogique</div>",
                unsafe_allow_html=True)

            # Le bouton de connexion bien rangé À L'INTÉRIEUR de la carte
            if st.button("Continuer avec Google", use_container_width=True):
                st.login()

            st.markdown(
                "<div style='text-align: center; color: #999; font-size: 11px; margin-top: 20px; margin-bottom: 10px;'>Connexion sécurisée avec Google</div>",
                unsafe_allow_html=True)

    st.stop()


# ============================================================
# 👤 UTILISATEUR CONNECTÉ
# ============================================================

user_email = getattr(st.user, "email", None)

username_connecte = (
    getattr(st.user, "name", None)
    or getattr(st.user, "given_name", None)
    or user_email
    or "Utilisateur"
)

# Sauvegarde de l'utilisateur dans la session
st.session_state.user_connecte = username_connecte
st.session_state.user_email = user_email

logger.info(
    f"👤 Utilisateur connecté : {username_connecte} "
    f"({user_email})"
)


# ============================================================
# 💾 ENREGISTREMENT DE L'UTILISATEUR EN BASE
# ============================================================

try:

    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username = ?",
        (user_email,)
    )

    utilisateur_existant = c.fetchone()

    if not utilisateur_existant:

        c.execute(
            """
            INSERT INTO users
            (username, password, solde_credits)
            VALUES (?, ?, ?)
            """,
            (
                user_email,
                "oauth_google",
                5
            )
        )

        conn.commit()

    conn.close()

except Exception as e:

    logger.warning(
        f"⚠️ Erreur enregistrement utilisateur : {e}"
    )


# ============================================================
# 📁 DOSSIER DES DISCUSSIONS
# ============================================================

st.session_state.dossier_discussions = (
    dossier_utilisateur(user_email)
)


# ============================================================
# 👤 PROFIL UTILISATEUR
# ============================================================

if "profil_utilisateur" not in st.session_state:

    st.session_state.profil_utilisateur = (
        charger_profil_utilisateur(user_email)
    )


# ============================================================
# 📄 FICHIER DE LA DISCUSSION COURANTE
# ============================================================

if "fichier_courant" not in st.session_state:

    st.session_state.fichier_courant = (
        nom_fichier_horodate(
            st.session_state.dossier_discussions
        )
    )


# ============================================================
# 💬 MESSAGES DE LA DISCUSSION
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []

# ==========================================
# ÉCRAN MEROUNG ACADEMY
# ==========================================
if st.session_state.mode_app == "academy" and st.session_state.academy_context is None:
    st.markdown("""
    <div class="academy-welcome">
        <h1>🎓 Meroung Academy</h1>
        <p>Bienvenue <strong>""" + username_connecte + """</strong></p>
        <p>Je suis Meroung AI, ton enseignant personnel</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Qui es-tu ?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👨‍🎓 Je suis élève", use_container_width=True, key="btn_eleve"):
            st.session_state.academy_step = "niveau_eleve"
            st.rerun()

    with col2:
        if st.button("👨‍👩‍👧 Je suis parent d'élève", use_container_width=True, key="btn_parent"):
            st.session_state.academy_step = "info_parent"
            st.rerun()

    st.markdown("""
    <div class="academy-info">
        <strong>💡 Meroung Academy</strong> est le mode enseignement personnalisé de Meroung AI.
        Je m'adapte à ton rôle pour t'aider de la meilleure façon possible.
    </div>
    """, unsafe_allow_html=True)

# --- Étape : Infos élève ---
if st.session_state.mode_app == "academy" and st.session_state.get("academy_step") == "niveau_eleve":
    st.markdown("### Tes informations")

    eleve_nom = st.text_input("Quel est ton nom ?", placeholder="Ex : Lucas", key="input_eleve_nom")

    niveaux = ["6ème", "5ème", "4ème", "3ème", "2nde", "1ère", "Terminale", "Licence", "Master", "Doctorat"]
    eleve_niveau = st.selectbox("Quel est ton niveau d'étude ?", niveaux, key="select_eleve_niveau")

    if st.button("✓ Continuer", use_container_width=True):
        if eleve_nom.strip():
            st.session_state.academy_context = {
                "role": "eleve",
                "nom": eleve_nom.strip(),
                "niveau": eleve_niveau
            }
            st.session_state.academy_step = None
            st.session_state.messages = [
                {"role": "model",
                 "text": f"Bienvenue sur Meroung Academy, {eleve_nom} ! 🎓\n\nJe suis Meroung AI, ton enseignant personnel.\n\nJe vais t'aider dans tes apprentissages de façon structurée et progressive. N'hésite pas à me poser des questions sur n'importe quel sujet !\n\nQuelle matière veux-tu étudier aujourd'hui ?"}
            ]
            st.rerun()
        else:
            st.error("⚠️ Remplis ton nom !")

# --- Étape : Infos parent ---
if st.session_state.mode_app == "academy" and st.session_state.get("academy_step") == "info_parent":
    st.markdown("### Infos pour mieux t'aider")

    parent_nom = st.text_input("Ton nom (ou surnom) :", placeholder="Ex : Marie", key="input_parent_nom")
    enfant_nom = st.text_input("Nom de ton enfant :", placeholder="Ex : Lucas", key="input_enfant_nom")

    classes = ["6ème", "5ème", "4ème", "3ème", "2nde", "1ère", "Terminale", "Licence", "Master", "Doctorat"]
    enfant_classe = st.selectbox("Classe de l'enfant :", classes, key="select_classe")

    if st.button("✓ Continuer", use_container_width=True):
        if parent_nom.strip() and enfant_nom.strip():
            st.session_state.academy_context = {
                "role": "parent",
                "parent_nom": parent_nom.strip(),
                "enfant_nom": enfant_nom.strip(),
                "enfant_classe": enfant_classe
            }
            st.session_state.academy_step = None
            st.session_state.messages = [
                {"role": "model",
                 "text": f"Bienvenue sur Meroung Academy, {parent_nom} ! 🎓\n\nJe suis Meroung AI, ton assistant pédagogique.\n\nJe vais t'aider à supporter l'apprentissage de {enfant_nom} ({enfant_classe}) de la meilleure façon possible.\n\nDans quelle matière ton enfant a besoin d'aide ?"}
            ]
            st.rerun()
        else:
            st.error("⚠️ Remplis tous les champs !")

# ==========================================
# BARRE LATÉRALE
# ==========================================
with st.sidebar:
    st.title(f"📌 {APP_NAME}")
    user_picture = getattr(st.user, "picture", None)
    if user_picture:
        try:
            st.image(user_picture, width=60)
        except:
            pass
    st.markdown(f"👤 **{username_connecte}**")
    st.caption("✨ Messages illimités")

    if st.button("Déconnexion", use_container_width=True):
        logger.info(f"👋 Déconnexion")
        # Streamlit Cloud gère la déconnexion automatiquement
        st.rerun()

    st.markdown("---")

    # --- BOUTON MEROUNG ACADEMY ---
    if st.session_state.mode_app == "general":
        if st.button("🎓 Lancer Meroung Academy", use_container_width=True, key="btn_academy"):
            st.session_state.mode_app = "academy"
            st.session_state.academy_context = None
            st.session_state.academy_step = None
            st.rerun()
    else:
        if st.button("↩️ Retour à Meroung AI", use_container_width=True, key="btn_general"):
            st.session_state.mode_app = "general"
            st.session_state.academy_context = None
            st.session_state.messages = [
                {"role": "model", "text": f"Salut {username_connecte}, qu'est-ce qu'on crée ou analysons aujourd'hui ?"}
            ]
            st.session_state.fichier_courant = nom_fichier_horodate(st.session_state.dossier_discussions)
            st.rerun()

    st.markdown("---")

    # --- PERSONNALISATION ---
    with st.expander("⚙️ Personnaliser"):
        profil = st.session_state.profil_utilisateur

        persona_input = st.text_area(
            "Instructions personnalisées",
            value=profil.get("persona", ""),
            placeholder="Exemple : réponds de façon concise...",
            height=80,
            key="input_persona",
        )
        memoire_input = st.text_area(
            "Mémoire (infos à retenir)",
            value=profil.get("memoire", ""),
            placeholder="Exemple : je suis développeur...",
            height=80,
            key="input_memoire",
        )

        if st.button("💾 Enregistrer", use_container_width=True):
            nouveau_profil = {
                "persona": persona_input.strip(),
                "memoire": memoire_input.strip(),
                "modele": GEMINI_MODEL,
                "langue_preference": "auto",
            }
            st.session_state.profil_utilisateur = nouveau_profil
            sauvegarder_profil_utilisateur(user_email, nouveau_profil)
            st.success("✅ Profil enregistré !")

    st.markdown("---")

    if st.button("✏️ Nouvelle discussion", use_container_width=True):
        if st.session_state.mode_app == "academy":
            st.session_state.messages = [
                {"role": "model", "text": f"Bienvenue sur Meroung Academy ! 🎓\n\nQuel sujet veux-tu étudier ?"}
            ]
        else:
            st.session_state.messages = [
                {"role": "model", "text": f"Salut {username_connecte}, qu'est-ce qu'on crée ou analysons aujourd'hui ?"}
            ]
        st.session_state.fichier_courant = nom_fichier_horodate(st.session_state.dossier_discussions)
        st.rerun()

    st.markdown("---")
    st.subheader("💬 Historique")
    dossier_actuel = st.session_state.dossier_discussions
    if os.path.exists(dossier_actuel):
        fichiers = sorted(os.listdir(dossier_actuel), reverse=True)
        for fichier in fichiers:
            if fichier.endswith(".json") and not fichier.startswith("_"):
                chemin_complet = os.path.join(dossier_actuel, fichier)

                try:
                    with open(chemin_complet, "r", encoding="utf-8") as f:
                        messages = json.load(f)
                    premier_msg = next((m["text"] for m in messages if m["role"] == "user"), "Discussion")
                    nom_affiche = premier_msg[:50].strip()
                    if len(premier_msg) > 50:
                        nom_affiche += "..."
                except:
                    nom_affiche = fichier.replace("chat_", "").replace(".json", "")

                col_charger, col_menu = st.columns([0.85, 0.15])

                with col_charger:
                    if st.button(f"💬 {nom_affiche}", key=f"load_{fichier}", use_container_width=True):
                        st.session_state.fichier_courant = chemin_complet
                        try:
                            with open(chemin_complet, "r", encoding="utf-8") as f:
                                st.session_state.messages = json.load(f)
                        except Exception:
                            pass
                        st.rerun()

                with col_menu:
                    with st.popover("⋮", help="Options"):
                        if st.button("✏️ Renommer", key=f"rename_btn_{fichier}"):
                            nouveau_nom = st.text_input("Nouveau nom", value=nom_affiche, key=f"rename_input_{fichier}")
                            if st.button("✓", key=f"rename_confirm_{fichier}"):
                                if nouveau_nom.strip():
                                    slug = re.sub(r"\s+", "_",
                                                  re.sub(r"[^a-z0-9\s-]", "", nouveau_nom.strip().lower()))[:50]
                                    nouveau_chemin = os.path.join(dossier_actuel, f"chat_{slug}.json")
                                    try:
                                        os.rename(chemin_complet, nouveau_chemin)
                                        if st.session_state.fichier_courant == chemin_complet:
                                            st.session_state.fichier_courant = nouveau_chemin
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur : {e}")

                        if st.button("🗑️ Supprimer", key=f"del_btn_{fichier}"):
                            try:
                                os.remove(chemin_complet)
                                if st.session_state.fichier_courant == chemin_complet:
                                    st.session_state.messages = [
                                        {"role": "model", "text": f"Salut {username_connecte}, c'est parti ?"}
                                    ]
                                    st.session_state.fichier_courant = nom_fichier_horodate(dossier_actuel)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur : {e}")

# ==========================================
# INTERFACE PRINCIPALE
# ==========================================

# Afficher les messages
for idx_message, message in enumerate(st.session_state.messages):
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        if message.get("type") == "image":
            st.image(message.get("url"), caption=message.get("text"))
        else:
            if message.get("text"):
                st.markdown(message.get("text", ""))
            for nom_fichier in message.get("fichiers_joints", []):
                st.caption(f"📎 {nom_fichier}")

        # Export PDF
        if message["role"] == "model" and message.get("type") != "image" and message.get("text"):
            try:
                pdf_bytes = generer_pdf_depuis_texte(f"Réponse — {APP_NAME}", message["text"])
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📄 PDF", data=pdf_bytes,
                        file_name=f"reponse_{idx_message}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{idx_message}",
                    )
                with col2:
                    if st.button("🔊", key=f"audio_{idx_message}", help="Écouter"):
                        lire_a_voix_haute(message["text"])
            except Exception as e:
                logger.warning(f"⚠️ Erreur PDF : {e}")

# --- MODE VOCAL ---
st.markdown("""
<style>
    .bouton-micro {
        position: fixed;
        right: 90px;
        bottom: 22px;
        z-index: 999;
    }
    .bouton-micro button {
        width: 44px;
        height: 44px;
        border-radius: 50% !important;
        background: #2563eb !important;
        color: white !important;
    }
    .bouton-micro.actif button {
        background: #dc2626 !important;
    }
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("mode_vocal_actif", False)

classe_micro = "bouton-micro actif" if st.session_state.mode_vocal_actif else "bouton-micro"
st.markdown(f'<div class="{classe_micro}">', unsafe_allow_html=True)
label_micro = "⏹️" if st.session_state.mode_vocal_actif else "🎤"
if st.button(label_micro, key="toggle_modal_vocal"):
    st.session_state.mode_vocal_actif = not st.session_state.mode_vocal_actif
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.mode_vocal_actif:
    st.info("🎙️ Mode vocal actif — parle pour converser")
    audio_micro = st.audio_input("", key=f"audio_{len(st.session_state.messages)}", label_visibility="collapsed")
    if audio_micro is not None:
        audio_bytes = audio_micro.getvalue()
        signature_audio = hash(audio_bytes)
        if st.session_state.get("dernier_audio_traite") != signature_audio:
            st.session_state.dernier_audio_traite = signature_audio
            st.session_state.messages.append({
                "role": "user",
                "text": "🎤 Message vocal",
                "fichiers_joints": ["message_vocal.wav"]
            })
            with st.chat_message("user", avatar="👤"):
                st.markdown("🎤 Message vocal")

            contenu_requete_audio = [
                "Transcris ce message vocal puis réponds-y naturellement.",
                {"mime_type": "audio/wav", "data": audio_bytes},
            ]
            st.session_state.prochaine_reponse_vocale = True
            logger.info("🎤 Message vocal traité")
            generer_et_ajouter_reponse("Message vocal", contenu_requete_audio)
            st.rerun()

# --- SAISIE CHAT ---
st.markdown("### 📝 Envoie un message ou une photo")

chat_input_value = st.chat_input(
    "Demander à Meroung...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "pdf", "txt", "py", "csv", "md"],
)

if chat_input_value:
    prompt = chat_input_value.text
    fichiers_joints = list(chat_input_value.files) if chat_input_value.files else []

    if not prompt.strip() and not fichiers_joints:
        st.error("Message ou fichier requis.")
        st.stop()

    if len(prompt) > MAX_INPUT_LENGTH:
        st.error(f"Message trop long (max {MAX_INPUT_LENGTH}).")
        st.stop()

    # Auto-renaming
    if len(st.session_state.messages) == 1 and prompt:
        try:
            chemin_actuel = st.session_state.fichier_courant
            nom_base = os.path.basename(chemin_actuel)
            if re.match(r"^chat_\d{8}_\d{6}\.json$", nom_base):
                horodatage = nom_base.replace("chat_", "").replace(".json", "")
                slug = re.sub(r"\s+", "_", re.sub(r"[^a-z0-9\s-]", "", prompt[:60].strip().lower()))
                nouveau_chemin = f"{st.session_state.dossier_discussions}/chat_{horodatage}_{slug}.json"
                os.rename(chemin_actuel, nouveau_chemin)
                st.session_state.fichier_courant = nouveau_chemin
        except Exception as e:
            logger.warning(f"⚠️ Erreur renaming : {e}")

    noms_fichiers_joints = [f.name for f in fichiers_joints]
    message_utilisateur = {"role": "user", "text": prompt}
    if noms_fichiers_joints:
        message_utilisateur["fichiers_joints"] = noms_fichiers_joints
    st.session_state.messages.append(message_utilisateur)

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        for f in noms_fichiers_joints:
            st.caption(f"📎 {f}")

    # --- ANALYSER LE TRAVAIL ACADEMY (PHOTOS) ---
    if st.session_state.mode_app == "academy" and st.session_state.academy_context and fichiers_joints:
        context = st.session_state.academy_context

        # Traiter seulement les images
        for f in fichiers_joints:
            if f.type and f.type.startswith("image"):
                try:
                    image_bytes = f.getvalue()
                    logger.info(f"🖼️ Photo de travail reçue : {f.name}")

                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown("### 📸 Analyse du travail reçu...")

                        # Analyser avec vision Gemini
                        reponse_complete = analyser_travail_eleve(image_bytes, context, prompt)

                        if reponse_complete:
                            st.session_state.messages.append({"role": "model", "text": reponse_complete})
                            logger.info("✅ Analyse terminée")
                except Exception as e:
                    logger.error(f"❌ Erreur traitement image : {e}")
                    st.error(f"Erreur : {e}")

        sauvegarder_discussion()
        st.rerun()

    # --- FLOW NORMAL (non-Academy ou pas de photos) ---
    contenu_requete = [prompt]

    for f in fichiers_joints:
        try:
            taille_mb = f.size / (1024 * 1024)
            if taille_mb > MAX_FILE_SIZE_MB:
                st.error(f"📎 {f.name} trop volumineux")
                logger.warning(f"⚠️ Fichier trop gros : {f.name}")
                continue

            if f.type and f.type.startswith("image"):
                img = Image.open(f)
                contenu_requete.append(img)
                contenu_requete.append(f"[Image : {f.name}]")
                logger.info(f"🖼️ Image jointe")
            elif f.type == "application/pdf":
                contenu_requete.append({"mime_type": "application/pdf", "data": f.getvalue()})
                logger.info(f"📄 PDF joint")
            else:
                contenu_texte = f.getvalue().decode("utf-8", errors="ignore")
                contenu_requete.append(f"Fichier {f.name} :\n{contenu_texte[:20000]}")
                logger.info(f"📄 Fichier texte joint")
        except Exception as e:
            logger.error(f"❌ Erreur fichier {f.name} : {e}")
            st.error(f"Erreur : {e}")

    generer_et_ajouter_reponse(prompt, contenu_requete)
    st.rerun()

logger.info("✅ Interface active")
