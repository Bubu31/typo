"""Gestionnaire de snippets (textes prédéfinis réutilisables)."""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from settings_manager import ensure_config_dir, get_config_dir


def get_snippets_path() -> Path:
    """Retourne le chemin du fichier snippets.json."""
    return get_config_dir() / "snippets.json"


# Structure par défaut pour snippets.json
DEFAULT_SNIPPETS_FILE = {
    "snippets": []
}


def load_snippets() -> List[Dict]:
    """
    Charge les snippets depuis snippets.json.

    Returns:
        Liste de snippets [{id, label, content, hotkey_slot}, ...].
    """
    snippets_path = get_snippets_path()

    if not snippets_path.exists():
        ensure_config_dir()
        save_snippets([])
        return []

    try:
        with open(snippets_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("snippets", [])
    except (json.JSONDecodeError, IOError):
        return []


def save_snippets(snippets: List[Dict]) -> None:
    """
    Sauvegarde les snippets dans snippets.json.

    Args:
        snippets: Liste de snippets.
    """
    ensure_config_dir()
    snippets_path = get_snippets_path()
    temp_path = snippets_path.with_suffix('.tmp')

    data = {"snippets": snippets}

    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_path.replace(snippets_path)
    except Exception as e:
        print(f"Erreur sauvegarde snippets: {e}")
        if temp_path.exists():
            temp_path.unlink()


def get_snippet(snippet_id: str) -> Optional[Dict]:
    """
    Récupère un snippet par son ID.

    Args:
        snippet_id: ID du snippet.

    Returns:
        Dict {id, label, content, hotkey_slot} ou None.
    """
    snippets = load_snippets()
    for snippet in snippets:
        if snippet.get("id") == snippet_id:
            return snippet.copy()
    return None


def get_snippet_by_slot(slot: int) -> Optional[Dict]:
    """
    Récupère le snippet assigné à un slot (1-9).

    Args:
        slot: Numéro de slot (1-9).

    Returns:
        Dict {id, label, content, hotkey_slot} ou None.
    """
    if not (1 <= slot <= 9):
        return None

    snippets = load_snippets()
    for snippet in snippets:
        if snippet.get("hotkey_slot") == slot:
            return snippet.copy()
    return None


def get_all_snippets() -> List[Dict]:
    """
    Retourne tous les snippets triés par label.

    Returns:
        Liste de snippets [{id, label, content, hotkey_slot}, ...].
    """
    snippets = load_snippets()
    return sorted(snippets, key=lambda s: s.get("label", "").lower())


def save_snippet(
    label: str,
    content: str,
    hotkey_slot: Optional[int] = None,
    snippet_id: Optional[str] = None
) -> str:
    """
    Ajoute ou met à jour un snippet.

    Args:
        label: Nom du snippet.
        content: Contenu du snippet.
        hotkey_slot: Slot 1-9 ou None.
        snippet_id: ID pour mise à jour, None pour création.

    Returns:
        ID du snippet (existant ou nouveau).
    """
    snippets = load_snippets()

    # Si hotkey_slot spécifié, vérifier qu'il est libre
    if hotkey_slot is not None:
        if not (1 <= hotkey_slot <= 9):
            hotkey_slot = None
        else:
            # Libérer le slot si déjà utilisé par un autre snippet
            for snippet in snippets:
                if snippet.get("id") != snippet_id and snippet.get("hotkey_slot") == hotkey_slot:
                    snippet["hotkey_slot"] = None

    # Mise à jour ou création
    if snippet_id:
        # Mise à jour
        for snippet in snippets:
            if snippet.get("id") == snippet_id:
                snippet["label"] = label
                snippet["content"] = content
                snippet["hotkey_slot"] = hotkey_slot
                save_snippets(snippets)
                return snippet_id
        # ID non trouvé, créer nouveau
        snippet_id = str(uuid.uuid4())
    else:
        # Nouveau snippet
        snippet_id = str(uuid.uuid4())

    new_snippet = {
        "id": snippet_id,
        "label": label,
        "content": content,
        "hotkey_slot": hotkey_slot
    }
    snippets.append(new_snippet)
    save_snippets(snippets)
    return snippet_id


def delete_snippet(snippet_id: str) -> bool:
    """
    Supprime un snippet.

    Args:
        snippet_id: ID du snippet à supprimer.

    Returns:
        True si supprimé, False si non trouvé.
    """
    snippets = load_snippets()
    initial_count = len(snippets)

    snippets = [s for s in snippets if s.get("id") != snippet_id]

    if len(snippets) < initial_count:
        save_snippets(snippets)
        return True
    return False


def search_snippets(query: str) -> List[Dict]:
    """
    Recherche des snippets par label ou contenu.

    Args:
        query: Terme de recherche.

    Returns:
        Liste de snippets correspondants, triés par pertinence.
    """
    if not query:
        return get_all_snippets()

    query_lower = query.lower()
    snippets = load_snippets()
    results = []

    for snippet in snippets:
        label = snippet.get("label", "").lower()
        content = snippet.get("content", "").lower()

        # Score de pertinence
        score = 0
        if query_lower in label:
            score += 10  # Match dans le label = haute priorité
            if label.startswith(query_lower):
                score += 5  # Commence par = encore plus prioritaire
        if query_lower in content:
            score += 1  # Match dans le contenu = basse priorité

        if score > 0:
            results.append((score, snippet))

    # Trier par score décroissant
    results.sort(key=lambda x: x[0], reverse=True)
    return [snippet for score, snippet in results]


def get_snippets_by_hotkey() -> Dict[int, Dict]:
    """
    Retourne un dict des snippets assignés à des hotkeys.

    Returns:
        Dict {slot: snippet_dict} pour slots 1-9.
    """
    snippets = load_snippets()
    by_hotkey = {}

    for snippet in snippets:
        slot = snippet.get("hotkey_slot")
        if slot and 1 <= slot <= 9:
            by_hotkey[slot] = snippet.copy()

    return by_hotkey


def is_slot_available(slot: int, exclude_id: Optional[str] = None) -> bool:
    """
    Vérifie si un slot hotkey est disponible.

    Args:
        slot: Numéro de slot (1-9).
        exclude_id: ID de snippet à exclure (pour édition).

    Returns:
        True si disponible, False sinon.
    """
    if not (1 <= slot <= 9):
        return False

    snippets = load_snippets()
    for snippet in snippets:
        if snippet.get("id") != exclude_id and snippet.get("hotkey_slot") == slot:
            return False

    return True
