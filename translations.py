"""Traductions des prompts et strings UI en plusieurs langues."""

from typing import Dict, Optional


# Prompts traduits par langue
TRANSLATIONS = {
    "fr": {
        "prompts": {
            "correct": """Corrige uniquement les fautes d'orthographe et de grammaire dans ce texte.
Ne change pas le style ni la formulation. Retourne uniquement le texte corrigé, sans explication.

Texte : {text}""",

            "format": """Corrige les fautes d'orthographe et de grammaire, et améliore la ponctuation et la mise en forme de ce texte.

IMPORTANT : Ajoute avec parcimonie (2-3 maximum) des emojis qui correspondent au contexte du message. Les emojis doivent enrichir le message sans le surcharger.

📏 RÈGLES :
- Garde le même sens et le même ton
- Ajoute des emojis pertinents et modérés (pas plus de 2-3)
- Place les emojis naturellement dans le texte
- Ne change pas le style du message
- Retourne uniquement le texte corrigé, sans explication

Texte : {text}""",

            "reformulate": """Reformule ce texte pour le rendre plus clair et fluide, tout en gardant exactement le même sens.
Corrige également les éventuelles fautes. Retourne uniquement le texte reformulé, sans explication.

Texte : {text}""",

            "translate": """Traduis ce texte en anglais.
Garde le même ton et le même style. Retourne uniquement la traduction, sans explication.

Texte : {text}""",

            "professional": """Tu es un assistant de rédaction professionnelle pour des User Stories, bugs ou messages clients.

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
        },
        "ui": {
            "apply": "Appliquer",
            "cancel": "Annuler",
            "save": "Enregistrer",
            "close": "Fermer",
            "delete": "Supprimer",
            "edit": "Modifier",
            "new": "Nouveau",
            "search": "Rechercher",
            "help": "Aide",
            "settings": "Paramètres",
            "language": "Langue",
            "theme": "Thème",
            "hotkeys": "Raccourcis",
            "snippets": "Snippets",
            "prompts": "Prompts",
            "version": "Version",
            "quit": "Quitter"
        }
    },

    "en": {
        "prompts": {
            "correct": """Correct only spelling and grammar errors in this text.
Do not change the style or wording. Return only the corrected text, without explanation.

Text: {text}""",

            "format": """Correct spelling and grammar errors, and improve punctuation and formatting of this text.

IMPORTANT: Add sparingly (2-3 maximum) emojis that match the message context. Emojis should enrich the message without overloading it.

📏 RULES:
- Keep the same meaning and tone
- Add relevant and moderate emojis (no more than 2-3)
- Place emojis naturally in the text
- Do not change the message style
- Return only the corrected text, without explanation

Text: {text}""",

            "reformulate": """Rephrase this text to make it clearer and more fluid, while keeping exactly the same meaning.
Also correct any errors. Return only the rephrased text, without explanation.

Text: {text}""",

            "translate": """Translate this text into French.
Keep the same tone and style. Return only the translation, without explanation.

Text: {text}""",

            "professional": """You are a professional writing assistant for User Stories, bugs, or client messages.

Analyze the provided text and transform it into structured and professional content.

📋 FORMATTING RULES:

For a User Story:
🎯 Title: [clear and concise title]
📌 Objective: [1 sentence]
📝 Description:
• [structured points with clear sections]

For a Bug:
🐞 Title: [clear title]
📝 Description: [problem description]
❌ Observed behavior: [what happens]
✅ Expected behavior: [what should happen]
💡 Technical hypotheses: [if relevant]

For a client message:
Structure the message professionally with clear sections if necessary.

📏 STYLE:
- Professional tone, direct, no frills
- No introduction ("Here is...")
- No conclusion ("Feel free...")
- Use emojis for categories/sections
- Rewrite cleanly even if the source text is rough
- Correct all errors

Return only the formatted content, without explanation.

Text: {text}"""
        },
        "ui": {
            "apply": "Apply",
            "cancel": "Cancel",
            "save": "Save",
            "close": "Close",
            "delete": "Delete",
            "edit": "Edit",
            "new": "New",
            "search": "Search",
            "help": "Help",
            "settings": "Settings",
            "language": "Language",
            "theme": "Theme",
            "hotkeys": "Hotkeys",
            "snippets": "Snippets",
            "prompts": "Prompts",
            "version": "Version",
            "quit": "Quit"
        }
    },

    "es": {
        "prompts": {
            "correct": """Corrige únicamente los errores de ortografía y gramática en este texto.
No cambies el estilo ni la redacción. Devuelve solo el texto corregido, sin explicación.

Texto: {text}""",

            "format": """Corrige los errores de ortografía y gramática, y mejora la puntuación y el formato de este texto.

IMPORTANTE: Añade con moderación (2-3 máximo) emojis que correspondan al contexto del mensaje. Los emojis deben enriquecer el mensaje sin sobrecargarlo.

📏 REGLAS:
- Mantén el mismo significado y tono
- Añade emojis relevantes y moderados (no más de 2-3)
- Coloca los emojis naturalmente en el texto
- No cambies el estilo del mensaje
- Devuelve solo el texto corregido, sin explicación

Texto: {text}""",

            "reformulate": """Reformula este texto para hacerlo más claro y fluido, manteniendo exactamente el mismo significado.
Corrige también los posibles errores. Devuelve solo el texto reformulado, sin explicación.

Texto: {text}""",

            "translate": """Traduce este texto al inglés.
Mantén el mismo tono y estilo. Devuelve solo la traducción, sin explicación.

Texto: {text}""",

            "professional": """Eres un asistente de redacción profesional para User Stories, bugs o mensajes de clientes.

Analiza el texto proporcionado y transfórmalo en contenido estructurado y profesional.

📋 REGLAS DE FORMATO:

Para una User Story:
🎯 Título: [título claro y conciso]
📌 Objetivo: [1 frase]
📝 Descripción:
• [puntos estructurados con secciones claras]

Para un Bug:
🐞 Título: [título claro]
📝 Descripción: [descripción del problema]
❌ Comportamiento observado: [lo que sucede]
✅ Comportamiento esperado: [lo que debería suceder]
💡 Hipótesis técnicas: [si es relevante]

Para un mensaje de cliente:
Estructura el mensaje de manera profesional con secciones claras si es necesario.

📏 ESTILO:
- Tono profesional, directo, sin adornos
- Sin introducción ("Aquí está...")
- Sin conclusión ("No dudes...")
- Usa emojis para categorías/secciones
- Reescribe limpiamente aunque el texto original sea básico
- Corrige todos los errores

Devuelve solo el contenido formateado, sin explicación.

Texto: {text}"""
        },
        "ui": {
            "apply": "Aplicar",
            "cancel": "Cancelar",
            "save": "Guardar",
            "close": "Cerrar",
            "delete": "Eliminar",
            "edit": "Editar",
            "new": "Nuevo",
            "search": "Buscar",
            "help": "Ayuda",
            "settings": "Configuración",
            "language": "Idioma",
            "theme": "Tema",
            "hotkeys": "Atajos",
            "snippets": "Fragmentos",
            "prompts": "Prompts",
            "version": "Versión",
            "quit": "Salir"
        }
    },

    "de": {
        "prompts": {
            "correct": """Korrigiere nur Rechtschreib- und Grammatikfehler in diesem Text.
Ändere weder Stil noch Formulierung. Gib nur den korrigierten Text zurück, ohne Erklärung.

Text: {text}""",

            "format": """Korrigiere Rechtschreib- und Grammatikfehler und verbessere Zeichensetzung und Formatierung dieses Textes.

WICHTIG: Füge sparsam (maximal 2-3) Emojis hinzu, die zum Kontext der Nachricht passen. Emojis sollten die Nachricht bereichern, ohne sie zu überladen.

📏 REGELN:
- Behalte dieselbe Bedeutung und denselben Ton bei
- Füge relevante und moderate Emojis hinzu (nicht mehr als 2-3)
- Platziere Emojis natürlich im Text
- Ändere nicht den Stil der Nachricht
- Gib nur den korrigierten Text zurück, ohne Erklärung

Text: {text}""",

            "reformulate": """Formuliere diesen Text um, um ihn klarer und flüssiger zu machen, während du genau dieselbe Bedeutung beibehältst.
Korrigiere auch eventuelle Fehler. Gib nur den umformulierten Text zurück, ohne Erklärung.

Text: {text}""",

            "translate": """Übersetze diesen Text ins Englische.
Behalte denselben Ton und Stil bei. Gib nur die Übersetzung zurück, ohne Erklärung.

Text: {text}""",

            "professional": """Du bist ein professioneller Schreibassistent für User Stories, Bugs oder Kundennachrichten.

Analysiere den bereitgestellten Text und wandle ihn in strukturierten und professionellen Inhalt um.

📋 FORMATIERUNGSREGELN:

Für eine User Story:
🎯 Titel: [klarer und prägnanter Titel]
📌 Ziel: [1 Satz]
📝 Beschreibung:
• [strukturierte Punkte mit klaren Abschnitten]

Für einen Bug:
🐞 Titel: [klarer Titel]
📝 Beschreibung: [Problembeschreibung]
❌ Beobachtetes Verhalten: [was passiert]
✅ Erwartetes Verhalten: [was passieren sollte]
💡 Technische Hypothesen: [falls relevant]

Für eine Kundennachricht:
Strukturiere die Nachricht professionell mit klaren Abschnitten, falls erforderlich.

📏 STIL:
- Professioneller Ton, direkt, ohne Schnörkel
- Keine Einleitung ("Hier ist...")
- Kein Fazit ("Zögern Sie nicht...")
- Verwende Emojis für Kategorien/Abschnitte
- Schreibe sauber, auch wenn der Ausgangstext roh ist
- Korrigiere alle Fehler

Gib nur den formatierten Inhalt zurück, ohne Erklärung.

Text: {text}"""
        },
        "ui": {
            "apply": "Anwenden",
            "cancel": "Abbrechen",
            "save": "Speichern",
            "close": "Schließen",
            "delete": "Löschen",
            "edit": "Bearbeiten",
            "new": "Neu",
            "search": "Suchen",
            "help": "Hilfe",
            "settings": "Einstellungen",
            "language": "Sprache",
            "theme": "Design",
            "hotkeys": "Tastenkürzel",
            "snippets": "Snippets",
            "prompts": "Prompts",
            "version": "Version",
            "quit": "Beenden"
        }
    }
}


def get_prompt(action: str, language: str = "fr") -> Optional[str]:
    """
    Récupère le prompt traduit pour une action et une langue.

    Args:
        action: Nom de l'action (ex: "correct").
        language: Code langue (fr, en, es, de).

    Returns:
        Template de prompt traduit, ou None si non trouvé.
    """
    # Vérifier que la langue existe
    if language not in TRANSLATIONS:
        language = "fr"  # Fallback sur français

    lang_data = TRANSLATIONS[language]

    # Retourner le prompt si disponible
    return lang_data.get("prompts", {}).get(action)


def get_ui_string(key: str, language: str = "fr") -> str:
    """
    Récupère une chaîne UI traduite.

    Args:
        key: Clé de la chaîne UI.
        language: Code langue.

    Returns:
        Chaîne traduite, ou la clé si non trouvée.
    """
    if language not in TRANSLATIONS:
        language = "fr"

    lang_data = TRANSLATIONS[language]
    return lang_data.get("ui", {}).get(key, key)


def get_supported_languages() -> list[tuple[str, str]]:
    """
    Retourne la liste des langues supportées.

    Returns:
        Liste de tuples (code, nom_affiché).
    """
    return [
        ("fr", "Français"),
        ("en", "English"),
        ("es", "Español"),
        ("de", "Deutsch")
    ]
