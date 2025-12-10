"""Gestionnaire centralisé des paramètres de l'application."""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


def get_config_dir() -> Path:
    """Retourne le répertoire de configuration dans %APPDATA%."""
    appdata = os.environ.get('APPDATA')
    if not appdata:
        # Fallback si APPDATA n'est pas défini
        appdata = Path.home() / "AppData" / "Roaming"
    return Path(appdata) / "Typo"


def ensure_config_dir() -> Path:
    """Crée le répertoire de configuration s'il n'existe pas."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Retourne le chemin du fichier config.json."""
    return get_config_dir() / "config.json"


def get_legacy_env_path() -> Path:
    """Retourne le chemin du fichier .env legacy (à côté de l'exe)."""
    if hasattr(os.sys, 'frozen'):
        # Exécutable PyInstaller
        return Path(os.sys.executable).parent / '.env'
    else:
        # Script Python
        return Path(__file__).parent / '.env'


# Configuration par défaut
DEFAULT_CONFIG = {
    "api_key": "",
    "language": "fr",
    "theme": "auto",
    "hotkeys": {
        "correct": {"ctrl": True, "alt": True, "key": "c"},
        "format": {"ctrl": True, "alt": True, "key": "f"},
        "reformulate": {"ctrl": True, "alt": True, "key": "r"},
        "professional": {"ctrl": True, "alt": True, "key": "p"},
        "translate": {"ctrl": True, "alt": True, "key": "t"},
        "help": {"ctrl": True, "alt": True, "key": "comma"},
        "snippet_1": {"ctrl": True, "alt": True, "key": "1"},
        "snippet_2": {"ctrl": True, "alt": True, "key": "2"},
        "snippet_3": {"ctrl": True, "alt": True, "key": "3"},
        "snippet_4": {"ctrl": True, "alt": True, "key": "4"},
        "snippet_5": {"ctrl": True, "alt": True, "key": "5"},
        "snippet_6": {"ctrl": True, "alt": True, "key": "6"},
        "snippet_7": {"ctrl": True, "alt": True, "key": "7"},
        "snippet_8": {"ctrl": True, "alt": True, "key": "8"},
        "snippet_9": {"ctrl": True, "alt": True, "key": "9"},
        "snippet_search": {"ctrl": True, "alt": True, "key": "s"}
    },
    "version": "1.3.0"
}


def migrate_from_env() -> Optional[str]:
    """
    Migre la clé API depuis le fichier .env legacy.

    Returns:
        La clé API si trouvée, None sinon.
    """
    env_path = get_legacy_env_path()
    if not env_path.exists():
        return None

    # Charger le .env
    load_dotenv(env_path)
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    return api_key


def load_config() -> Dict[str, Any]:
    """
    Charge la configuration depuis config.json.
    Si le fichier n'existe pas, tente une migration depuis .env.

    Returns:
        Dict de configuration (merged avec defaults).
    """
    config_path = get_config_path()

    # Si config.json n'existe pas, tenter migration
    if not config_path.exists():
        # Créer le répertoire
        ensure_config_dir()

        # Tenter migration depuis .env
        api_key = migrate_from_env()

        # Créer config avec defaults
        config = DEFAULT_CONFIG.copy()
        if api_key:
            config["api_key"] = api_key

        # Sauvegarder
        save_config(config)
        return config

    # Charger config.json existant
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Merger avec defaults pour ajouter nouvelles clés
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)

        # Merger hotkeys séparément pour ne pas perdre les customs
        if "hotkeys" in config:
            default_hotkeys = DEFAULT_CONFIG["hotkeys"].copy()
            default_hotkeys.update(config["hotkeys"])
            merged_config["hotkeys"] = default_hotkeys

        return merged_config

    except (json.JSONDecodeError, IOError) as e:
        # Config corrompu, utiliser defaults
        print(f"Erreur lecture config.json: {e}")
        print("Utilisation de la configuration par défaut")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """
    Sauvegarde la configuration dans config.json.
    Utilise une écriture atomique (temp file + rename).

    Args:
        config: Dict de configuration à sauvegarder.
    """
    ensure_config_dir()
    config_path = get_config_path()
    temp_path = config_path.with_suffix('.tmp')

    try:
        # Écrire dans fichier temporaire
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Rename atomique
        temp_path.replace(config_path)

    except Exception as e:
        print(f"Erreur sauvegarde config: {e}")
        # Nettoyer le fichier temp si existe
        if temp_path.exists():
            temp_path.unlink()


# Instance globale de configuration (singleton pattern)
_config_cache: Optional[Dict[str, Any]] = None


def get_config() -> Dict[str, Any]:
    """
    Retourne la configuration actuelle (avec cache).

    Returns:
        Dict de configuration.
    """
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config()
    return _config_cache


def reload_config() -> Dict[str, Any]:
    """
    Recharge la configuration depuis le fichier (invalide le cache).

    Returns:
        Dict de configuration rechargée.

    Raises:
        json.JSONDecodeError: Si le fichier JSON est invalide.
        IOError: Si le fichier ne peut pas être lu.
    """
    global _config_cache
    config_path = get_config_path()

    if not config_path.exists():
        # Créer avec defaults si n'existe pas
        _config_cache = load_config()
        return _config_cache

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Merger avec defaults
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)

        if "hotkeys" in config:
            default_hotkeys = DEFAULT_CONFIG["hotkeys"].copy()
            default_hotkeys.update(config["hotkeys"])
            merged_config["hotkeys"] = default_hotkeys

        _config_cache = merged_config
        return _config_cache

    except (json.JSONDecodeError, IOError) as e:
        # Propager l'erreur pour notification utilisateur
        raise


def get(key: str, default: Any = None) -> Any:
    """
    Récupère une valeur de configuration.

    Args:
        key: Clé de configuration (peut utiliser notation pointée, ex: "hotkeys.correct").
        default: Valeur par défaut si clé non trouvée.

    Returns:
        Valeur de configuration ou default.
    """
    config = get_config()

    # Support notation pointée (ex: "hotkeys.correct")
    keys = key.split('.')
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def set(key: str, value: Any) -> None:
    """
    Définit une valeur de configuration et sauvegarde.

    Args:
        key: Clé de configuration (peut utiliser notation pointée).
        value: Nouvelle valeur.
    """
    config = get_config()

    # Support notation pointée
    keys = key.split('.')
    target = config
    for k in keys[:-1]:
        if k not in target:
            target[k] = {}
        target = target[k]

    target[keys[-1]] = value

    # Sauvegarder
    save_config(config)

    # Mettre à jour le cache
    global _config_cache
    _config_cache = config


def get_api_key() -> Optional[str]:
    """
    Récupère la clé API.

    Returns:
        Clé API ou None si non configurée.
    """
    api_key = get("api_key", "")
    return api_key if api_key else None


def set_api_key(api_key: str) -> None:
    """
    Définit la clé API.

    Args:
        api_key: Nouvelle clé API.
    """
    set("api_key", api_key)
    # Mettre à jour également dans l'environnement pour compatibilité
    os.environ['ANTHROPIC_API_KEY'] = api_key
