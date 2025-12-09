"""Configuration centralisée du correcteur orthographique."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def get_app_dir() -> Path:
    """Retourne le répertoire de l'application (à côté de l'exe ou du script)."""
    if getattr(sys, 'frozen', False):
        # Exécutable PyInstaller
        return Path(sys.executable).parent
    else:
        # Script Python
        return Path(__file__).parent


def get_env_path() -> Path:
    """Retourne le chemin du fichier .env."""
    return get_app_dir() / '.env'


# Charger le fichier .env s'il existe
env_path = get_env_path()
if env_path.exists():
    load_dotenv(env_path)

# API Claude
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
MODEL = "claude-haiku-4-5-20251001"


def save_api_key(api_key: str) -> None:
    """Sauvegarde la clé API dans le fichier .env."""
    env_path = get_env_path()
    with open(env_path, 'w') as f:
        f.write(f'ANTHROPIC_API_KEY={api_key}\n')
    # Mettre à jour la variable globale
    global ANTHROPIC_API_KEY
    ANTHROPIC_API_KEY = api_key
    os.environ['ANTHROPIC_API_KEY'] = api_key

# Délai après Ctrl+C pour que le clipboard soit mis à jour (en secondes)
CLIPBOARD_DELAY = 0.25

# Délai avant de coller après fermeture du popup (en secondes)
PASTE_DELAY = 0.1

# Raccourcis clavier (format pynput)
HOTKEYS = {
    '<ctrl>+<alt>+c': 'correct',
    '<ctrl>+<alt>+f': 'format',
    '<ctrl>+<alt>+r': 'reformulate',
    '<ctrl>+<alt>+p': 'professional',
    '<ctrl>+<alt>+,': 'help',
}

# Labels pour l'interface
ACTION_LABELS = {
    'correct': 'Correction',
    'format': 'Correction + Formatage',
    'reformulate': 'Reformulation',
    'professional': 'Rédaction US/Bug/Message',
}

# Prompts pour l'API Claude
PROMPTS = {
    'correct': """Corrige uniquement les fautes d'orthographe et de grammaire dans ce texte.
Ne change pas le style ni la formulation. Retourne uniquement le texte corrigé, sans explication.

Texte : {text}""",

    'format': """Corrige les fautes d'orthographe et de grammaire, et améliore la ponctuation et la mise en forme de ce texte.
Garde le même sens et le même ton. Retourne uniquement le texte corrigé, sans explication.

Texte : {text}""",

    'reformulate': """Reformule ce texte pour le rendre plus clair et fluide, tout en gardant exactement le même sens.
Corrige également les éventuelles fautes. Retourne uniquement le texte reformulé, sans explication.

Texte : {text}""",

    'translate': """Traduis ce texte en anglais.
Garde le même ton et le même style. Retourne uniquement la traduction, sans explication.

Texte : {text}""",

    'professional': """Tu es un assistant de rédaction professionnelle pour des User Stories, bugs ou messages clients.

Analyse le texte fourni et transforme-le en contenu structuré et professionnel.

📋 RÈGLES DE FORMATAGE :

Pour une User Story :
🎯 Titre : [titre clair et concis]
📌 Objectif : [1 phrase]
📝 Description :
• [points structurés avec des sections claires]

Pour un Bug :
🐞 Titre : [titre clair]
📝 Description : [description du problème]
❌ Comportement observé : [ce qui se passe]
✅ Comportement attendu : [ce qui devrait se passer]
💡 Hypothèses techniques : [si pertinent]

Pour un message client :
Structure le message de manière professionnelle avec des sections claires si nécessaire.

📏 STYLE :
- Ton professionnel, direct, sans fioritures
- Pas d'introduction ("Voici...")
- Pas de conclusion ("N'hésite pas...")
- Utilise des emojis pour les catégories/sections
- Réécris proprement même si le texte source est brut
- Corrige toutes les fautes

Retourne uniquement le contenu formaté, sans explication.

Texte : {text}"""
}
