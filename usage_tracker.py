"""Suivi de l'utilisation de l'API Claude."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from config import get_app_dir

# Pricing Claude Haiku 4.5 (par million de tokens)
# Source: https://www.anthropic.com/pricing
PRICE_INPUT_PER_MILLION = 0.25  # $0.25 per 1M input tokens
PRICE_OUTPUT_PER_MILLION = 1.25  # $1.25 per 1M output tokens


def get_usage_file_path() -> Path:
    """Retourne le chemin du fichier de suivi d'utilisation."""
    from settings_manager import get_config_dir
    return get_config_dir() / 'usage_stats.json'


def migrate_usage_file_if_needed() -> None:
    """Migre usage_stats.json de l'exe dir vers AppData si nécessaire."""
    from config import get_app_dir
    from settings_manager import ensure_config_dir

    old_path = get_app_dir() / 'usage_stats.json'
    new_path = get_usage_file_path()

    # Si le nouveau fichier existe déjà, rien à faire
    if new_path.exists():
        return

    # Si l'ancien fichier existe, le déplacer
    if old_path.exists():
        try:
            ensure_config_dir()
            import shutil
            shutil.copy2(old_path, new_path)  # Copier
            old_path.unlink()  # Supprimer ancien
        except Exception as e:
            print(f"Avertissement: impossible de migrer usage_stats.json: {e}")
            # Continuer - nouveau fichier sera créé


def get_current_month() -> str:
    """Retourne le mois actuel au format YYYY-MM."""
    return datetime.now().strftime("%Y-%m")


def load_usage_stats() -> Dict[str, Any]:
    """
    Charge les statistiques d'utilisation depuis le fichier JSON.

    Returns:
        Dictionnaire contenant les stats. Réinitialise si nouveau mois.
    """
    # Migrer le fichier si nécessaire (première fois)
    migrate_usage_file_if_needed()

    usage_file = get_usage_file_path()
    current_month = get_current_month()

    # Valeurs par défaut
    default_stats = {
        "requests_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "month": current_month,
        "last_updated": datetime.now().isoformat()
    }

    # Si le fichier n'existe pas, retourner les valeurs par défaut
    if not usage_file.exists():
        save_usage_stats(default_stats)
        return default_stats

    try:
        with open(usage_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        # Si on est dans un nouveau mois, réinitialiser
        if stats.get("month") != current_month:
            stats = default_stats.copy()
            save_usage_stats(stats)

        return stats

    except (json.JSONDecodeError, IOError):
        # En cas d'erreur, retourner les valeurs par défaut
        return default_stats


def save_usage_stats(stats: Dict[str, Any]) -> None:
    """
    Sauvegarde les statistiques d'utilisation dans le fichier JSON.

    Args:
        stats: Dictionnaire contenant les stats à sauvegarder.
    """
    usage_file = get_usage_file_path()
    stats["last_updated"] = datetime.now().isoformat()

    try:
        with open(usage_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except IOError:
        pass  # Ignorer les erreurs d'écriture


def track_request(input_tokens: int, output_tokens: int) -> None:
    """
    Enregistre une nouvelle requête API.

    Args:
        input_tokens: Nombre de tokens en entrée.
        output_tokens: Nombre de tokens en sortie.
    """
    stats = load_usage_stats()
    stats["requests_count"] += 1
    stats["input_tokens"] += input_tokens
    stats["output_tokens"] += output_tokens
    save_usage_stats(stats)


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calcule le coût estimé en dollars.

    Args:
        input_tokens: Nombre de tokens en entrée.
        output_tokens: Nombre de tokens en sortie.

    Returns:
        Coût estimé en dollars.
    """
    input_cost = (input_tokens / 1_000_000) * PRICE_INPUT_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MILLION
    return input_cost + output_cost


def get_usage_summary() -> Dict[str, Any]:
    """
    Retourne un résumé de l'utilisation du mois en cours.

    Returns:
        Dictionnaire avec les stats et le coût estimé.
    """
    stats = load_usage_stats()
    total_cost = calculate_cost(stats["input_tokens"], stats["output_tokens"])

    return {
        "requests_count": stats["requests_count"],
        "input_tokens": stats["input_tokens"],
        "output_tokens": stats["output_tokens"],
        "total_tokens": stats["input_tokens"] + stats["output_tokens"],
        "estimated_cost": total_cost,
        "month": stats["month"]
    }


def reset_monthly_stats() -> None:
    """Réinitialise les statistiques mensuelles (pour tests ou reset manuel)."""
    default_stats = {
        "requests_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "month": get_current_month(),
        "last_updated": datetime.now().isoformat()
    }
    save_usage_stats(default_stats)


def format_usage_display() -> str:
    """
    Formate l'utilisation pour l'affichage dans le menu tray.

    Returns:
        Chaîne formatée (ex: "150 req • ~$2.50").
    """
    summary = get_usage_summary()
    requests = summary["requests_count"]
    cost = summary["estimated_cost"]

    # Formater le coût avec 2 décimales
    if cost < 0.01:
        cost_str = "<$0.01"
    else:
        cost_str = f"~${cost:.2f}"

    return f"{requests} req • {cost_str}"
