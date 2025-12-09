"""Gestionnaire de prompts personnalisés et par défaut."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from settings_manager import ensure_config_dir, get_config_dir
from config import PROMPTS as DEFAULT_PROMPTS


def get_prompts_path() -> Path:
    """Retourne le chemin du fichier prompts.json."""
    return get_config_dir() / "prompts.json"


# Structure par défaut pour prompts.json
DEFAULT_PROMPTS_FILE = {
    "custom": {},
    "overrides": {}
}


def load_prompts_file() -> Dict:
    """
    Charge le fichier prompts.json.

    Returns:
        Dict avec custom prompts et overrides.
    """
    prompts_path = get_prompts_path()

    if not prompts_path.exists():
        # Créer le fichier avec structure par défaut
        ensure_config_dir()
        save_prompts_file(DEFAULT_PROMPTS_FILE)
        return DEFAULT_PROMPTS_FILE.copy()

    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Fichier corrompu, retourner default
        return DEFAULT_PROMPTS_FILE.copy()


def save_prompts_file(prompts_data: Dict) -> None:
    """
    Sauvegarde le fichier prompts.json.

    Args:
        prompts_data: Dict avec custom prompts et overrides.
    """
    ensure_config_dir()
    prompts_path = get_prompts_path()
    temp_path = prompts_path.with_suffix('.tmp')

    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
        temp_path.replace(prompts_path)
    except Exception as e:
        print(f"Erreur sauvegarde prompts: {e}")
        if temp_path.exists():
            temp_path.unlink()


def get_prompt(action: str) -> Optional[str]:
    """
    Récupère le prompt pour une action donnée.
    Priorité : override > custom > default.

    Args:
        action: Nom de l'action (ex: "correct", "summarize").

    Returns:
        Template de prompt, ou None si non trouvé.
    """
    prompts_data = load_prompts_file()

    # 1. Vérifier les overrides pour actions par défaut
    if action in prompts_data.get("overrides", {}):
        override = prompts_data["overrides"][action]
        if override is not None:
            return override

    # 2. Vérifier les custom prompts
    if action in prompts_data.get("custom", {}):
        custom = prompts_data["custom"][action]
        if custom.get("enabled", True):
            return custom.get("prompt")

    # 3. Fallback sur default
    if action in DEFAULT_PROMPTS:
        return DEFAULT_PROMPTS[action]

    return None


def get_all_actions() -> List[str]:
    """
    Retourne la liste de toutes les actions disponibles.
    Inclut actions par défaut + custom prompts activés.

    Returns:
        Liste des noms d'actions.
    """
    actions = set()

    # Ajouter actions par défaut
    actions.update(DEFAULT_PROMPTS.keys())

    # Ajouter custom prompts activés
    prompts_data = load_prompts_file()
    for action_id, custom_data in prompts_data.get("custom", {}).items():
        if custom_data.get("enabled", True):
            actions.add(action_id)

    return sorted(actions)


def get_action_label(action: str) -> str:
    """
    Retourne le label d'affichage pour une action.

    Args:
        action: Nom de l'action.

    Returns:
        Label lisible.
    """
    from config import ACTION_LABELS

    # Vérifier d'abord les labels par défaut
    if action in ACTION_LABELS:
        return ACTION_LABELS[action]

    # Vérifier les custom prompts
    prompts_data = load_prompts_file()
    if action in prompts_data.get("custom", {}):
        return prompts_data["custom"][action].get("label", action)

    return action


def save_custom_prompt(action_id: str, label: str, prompt: str, enabled: bool = True) -> bool:
    """
    Ajoute ou met à jour un prompt personnalisé.

    Args:
        action_id: Identifiant unique de l'action (slug).
        label: Label d'affichage.
        prompt: Template de prompt (doit contenir {text}).
        enabled: Si True, le prompt est activé.

    Returns:
        True si succès, False si erreur de validation.
    """
    # Validation : le prompt doit contenir {text}
    if "{text}" not in prompt:
        return False

    # Charger les prompts
    prompts_data = load_prompts_file()

    # Ajouter/mettre à jour dans custom
    if "custom" not in prompts_data:
        prompts_data["custom"] = {}

    prompts_data["custom"][action_id] = {
        "label": label,
        "prompt": prompt,
        "enabled": enabled
    }

    # Sauvegarder
    save_prompts_file(prompts_data)
    return True


def delete_custom_prompt(action_id: str) -> bool:
    """
    Supprime un prompt personnalisé.

    Args:
        action_id: Identifiant du prompt à supprimer.

    Returns:
        True si supprimé, False si non trouvé.
    """
    prompts_data = load_prompts_file()

    if action_id in prompts_data.get("custom", {}):
        del prompts_data["custom"][action_id]
        save_prompts_file(prompts_data)
        return True

    return False


def toggle_custom_prompt(action_id: str) -> bool:
    """
    Active/désactive un prompt personnalisé.

    Args:
        action_id: Identifiant du prompt.

    Returns:
        Nouvel état (True=activé, False=désactivé), ou False si non trouvé.
    """
    prompts_data = load_prompts_file()

    if action_id in prompts_data.get("custom", {}):
        current_state = prompts_data["custom"][action_id].get("enabled", True)
        prompts_data["custom"][action_id]["enabled"] = not current_state
        save_prompts_file(prompts_data)
        return not current_state

    return False


def save_override(action: str, prompt: Optional[str]) -> bool:
    """
    Override un prompt par défaut.

    Args:
        action: Action par défaut (ex: "correct").
        prompt: Nouveau template, ou None pour réinitialiser.

    Returns:
        True si succès, False si erreur de validation.
    """
    # Validation si prompt fourni
    if prompt is not None and "{text}" not in prompt:
        return False

    # Vérifier que l'action existe dans les defaults
    if action not in DEFAULT_PROMPTS:
        return False

    prompts_data = load_prompts_file()

    if "overrides" not in prompts_data:
        prompts_data["overrides"] = {}

    prompts_data["overrides"][action] = prompt
    save_prompts_file(prompts_data)
    return True


def reset_to_default(action: str) -> bool:
    """
    Réinitialise un prompt par défaut (supprime l'override).

    Args:
        action: Action par défaut.

    Returns:
        True si réinitialisé, False si pas d'override.
    """
    return save_override(action, None)


def is_default_action(action: str) -> bool:
    """
    Vérifie si une action fait partie des actions par défaut.

    Args:
        action: Nom de l'action.

    Returns:
        True si action par défaut, False sinon.
    """
    return action in DEFAULT_PROMPTS


def has_override(action: str) -> bool:
    """
    Vérifie si une action par défaut a un override.

    Args:
        action: Nom de l'action.

    Returns:
        True si override existe, False sinon.
    """
    prompts_data = load_prompts_file()
    overrides = prompts_data.get("overrides", {})
    return action in overrides and overrides[action] is not None


def get_custom_prompts() -> Dict[str, Dict]:
    """
    Retourne tous les prompts personnalisés.

    Returns:
        Dict {action_id: {label, prompt, enabled}}.
    """
    prompts_data = load_prompts_file()
    return prompts_data.get("custom", {}).copy()
