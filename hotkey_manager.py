"""Gestionnaire de validation et conversion des raccourcis clavier."""

from typing import Dict, List, Optional, Set, Tuple
import settings_manager


# Mapping des caractères vers les VK codes Windows
CHAR_TO_VK = {
    'a': 65, 'b': 66, 'c': 67, 'd': 68, 'e': 69, 'f': 70, 'g': 71, 'h': 72,
    'i': 73, 'j': 74, 'k': 75, 'l': 76, 'm': 77, 'n': 78, 'o': 79, 'p': 80,
    'q': 81, 'r': 82, 's': 83, 't': 84, 'u': 85, 'v': 86, 'w': 87, 'x': 88,
    'y': 89, 'z': 90,
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55,
    '8': 56, '9': 57,
    'comma': 188,  # ,
    'period': 190,  # .
    'semicolon': 186,  # ;
    'minus': 189,  # -
    'equals': 187,  # =
    'slash': 191,  # /
    'backslash': 220,  # \
    'space': 32
}

# VK codes vers caractères (reverse mapping)
VK_TO_CHAR = {v: k for k, v in CHAR_TO_VK.items()}

# Raccourcis système réservés (ne pas autoriser)
RESERVED_COMBINATIONS = {
    # Windows shortcuts
    ('ctrl', 'alt', 'del'),
    ('alt', 'tab'),
    ('ctrl', 'esc'),
    ('win',),  # Touche Windows seule
}


def parse_hotkey(hotkey_config: Dict[str, any]) -> Optional[int]:
    """
    Convertit une configuration de hotkey en VK code.

    Args:
        hotkey_config: Dict avec clés "ctrl", "alt", "shift" (bool) et "key" (str).

    Returns:
        VK code de la touche, ou None si invalide.

    Example:
        >>> parse_hotkey({"ctrl": True, "alt": True, "key": "c"})
        67
    """
    key = hotkey_config.get("key", "").lower()

    if not key:
        return None

    return CHAR_TO_VK.get(key)


def format_hotkey_display(hotkey_config: Dict[str, any]) -> str:
    """
    Formate un hotkey config en string lisible pour l'affichage.

    Args:
        hotkey_config: Dict avec clés "ctrl", "alt", "shift", "key".

    Returns:
        String formaté, ex: "Ctrl+Alt+C".

    Example:
        >>> format_hotkey_display({"ctrl": True, "alt": True, "key": "c"})
        "Ctrl+Alt+C"
    """
    parts = []

    if hotkey_config.get("ctrl"):
        parts.append("Ctrl")
    if hotkey_config.get("alt"):
        parts.append("Alt")
    if hotkey_config.get("shift"):
        parts.append("Shift")

    key = hotkey_config.get("key", "").lower()
    if key:
        # Formatter la touche (majuscule si lettre, nom complet si spécial)
        key_display = {
            'comma': ',',
            'period': '.',
            'semicolon': ';',
            'minus': '-',
            'equals': '=',
            'slash': '/',
            'backslash': '\\',
            'space': 'Space'
        }.get(key, key.upper())

        parts.append(key_display)

    return "+".join(parts)


def validate_hotkey(hotkey_config: Dict[str, any]) -> Tuple[bool, str]:
    """
    Valide un hotkey config.

    Args:
        hotkey_config: Dict avec clés "ctrl", "alt", "shift", "key".

    Returns:
        Tuple (is_valid, error_message).

    Example:
        >>> validate_hotkey({"ctrl": True, "alt": True, "key": "c"})
        (True, "")
    """
    # Vérifier qu'il y a au moins un modificateur
    has_modifier = (
        hotkey_config.get("ctrl", False) or
        hotkey_config.get("alt", False) or
        hotkey_config.get("shift", False)
    )

    if not has_modifier:
        return False, "Un raccourci doit contenir au moins Ctrl, Alt ou Shift"

    # Vérifier que la touche est valide
    key = hotkey_config.get("key", "").lower()
    if not key:
        return False, "Aucune touche spécifiée"

    if key not in CHAR_TO_VK:
        return False, f"Touche '{key}' non reconnue"

    # Vérifier que ce n'est pas un raccourci système réservé
    modifiers = set()
    if hotkey_config.get("ctrl"):
        modifiers.add("ctrl")
    if hotkey_config.get("alt"):
        modifiers.add("alt")
    if hotkey_config.get("shift"):
        modifiers.add("shift")

    # Créer tuple pour vérification
    combo = tuple(sorted(modifiers))
    if combo in RESERVED_COMBINATIONS:
        return False, "Ce raccourci est réservé par le système"

    return True, ""


def check_conflicts(
    hotkey_config: Dict[str, any],
    exclude_action: Optional[str] = None
) -> List[str]:
    """
    Vérifie si un hotkey config est en conflit avec les hotkeys existants.

    Args:
        hotkey_config: Dict avec clés "ctrl", "alt", "shift", "key".
        exclude_action: Action à exclure de la vérification (pour édition).

    Returns:
        Liste des actions en conflit.

    Example:
        >>> check_conflicts({"ctrl": True, "alt": True, "key": "c"}, exclude_action="format")
        ["correct"]  # Si "correct" utilise déjà Ctrl+Alt+C
    """
    conflicts = []

    # Récupérer tous les hotkeys actuels
    all_hotkeys = settings_manager.get("hotkeys", {})

    # Créer une signature unique pour le hotkey testé
    test_signature = _hotkey_signature(hotkey_config)

    for action, existing_config in all_hotkeys.items():
        # Skip l'action à exclure
        if action == exclude_action:
            continue

        # Comparer les signatures
        if _hotkey_signature(existing_config) == test_signature:
            conflicts.append(action)

    return conflicts


def _hotkey_signature(hotkey_config: Dict[str, any]) -> str:
    """
    Crée une signature unique pour un hotkey config.

    Args:
        hotkey_config: Dict avec clés "ctrl", "alt", "shift", "key".

    Returns:
        String signature unique.
    """
    parts = []
    if hotkey_config.get("ctrl"):
        parts.append("ctrl")
    if hotkey_config.get("alt"):
        parts.append("alt")
    if hotkey_config.get("shift"):
        parts.append("shift")
    parts.append(hotkey_config.get("key", "").lower())
    return "+".join(parts)


def get_all_hotkeys() -> Dict[str, Dict[str, any]]:
    """
    Retourne tous les hotkeys actuellement configurés.

    Returns:
        Dict {action: hotkey_config}.
    """
    return settings_manager.get("hotkeys", {})


def update_hotkey(action: str, hotkey_config: Dict[str, any]) -> Tuple[bool, str]:
    """
    Met à jour un hotkey après validation.

    Args:
        action: Nom de l'action (ex: "correct").
        hotkey_config: Nouveau hotkey config.

    Returns:
        Tuple (success, error_message).
    """
    # Valider le hotkey
    is_valid, error = validate_hotkey(hotkey_config)
    if not is_valid:
        return False, error

    # Vérifier les conflits
    conflicts = check_conflicts(hotkey_config, exclude_action=action)
    if conflicts:
        conflict_names = ", ".join(conflicts)
        return False, f"Conflit avec : {conflict_names}"

    # Mettre à jour
    settings_manager.set(f"hotkeys.{action}", hotkey_config)
    return True, ""


def reset_to_defaults() -> None:
    """Réinitialise tous les hotkeys aux valeurs par défaut."""
    from settings_manager import DEFAULT_CONFIG
    default_hotkeys = DEFAULT_CONFIG["hotkeys"].copy()
    settings_manager.set("hotkeys", default_hotkeys)


def get_action_label(action: str) -> str:
    """
    Retourne le label d'affichage pour une action.

    Args:
        action: Nom de l'action.

    Returns:
        Label lisible.
    """
    labels = {
        "correct": "Corriger",
        "format": "Formater",
        "reformulate": "Reformuler",
        "professional": "Rédiger US/Bug/Message",
        "translate": "Traduire en anglais",
        "help": "Afficher l'aide",
        "snippet_1": "Snippet 1",
        "snippet_2": "Snippet 2",
        "snippet_3": "Snippet 3",
        "snippet_4": "Snippet 4",
        "snippet_5": "Snippet 5",
        "snippet_6": "Snippet 6",
        "snippet_7": "Snippet 7",
        "snippet_8": "Snippet 8",
        "snippet_9": "Snippet 9",
        "snippet_search": "Rechercher un snippet"
    }
    return labels.get(action, action)
