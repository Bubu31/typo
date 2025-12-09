"""Gestionnaire de thèmes avec détection automatique du thème Windows."""

import winreg
from typing import Dict, Literal


# Définition des palettes de couleurs
THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "fg": "#000000",
        "bg_secondary": "#F5F5F5",
        "fg_secondary": "#666666",
        "accent": "#4CAF50",
        "border": "#CCCCCC",
        "button_bg": "#F0F0F0",
        "button_fg": "#000000",
        "button_active_bg": "#E0E0E0",
        "tray_icon_color": "#4CAF50",
        "tray_icon_inactive": "#9E9E9E",
        "text_cursor": "#000000"
    },
    "dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",
        "bg_secondary": "#2D2D2D",
        "fg_secondary": "#AAAAAA",
        "accent": "#4CAF50",
        "border": "#444444",
        "button_bg": "#3C3C3C",
        "button_fg": "#FFFFFF",
        "button_active_bg": "#4A4A4A",
        "tray_icon_color": "#60D060",
        "tray_icon_inactive": "#666666",
        "text_cursor": "#FFFFFF"
    }
}


def detect_windows_theme() -> Literal["light", "dark"]:
    """
    Détecte le thème Windows actuel via le Registry.

    Returns:
        "light" ou "dark" selon le thème système.
    """
    try:
        # Ouvrir la clé de registre pour le thème
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            registry_path,
            0,
            winreg.KEY_READ
        )

        # Lire la valeur AppsUseLightTheme
        # 1 = Light theme, 0 = Dark theme
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)

        return "light" if value == 1 else "dark"

    except (FileNotFoundError, OSError):
        # Si impossible de lire le registre, utiliser light par défaut
        return "light"


def get_theme_colors(theme_name: Literal["light", "dark"]) -> Dict[str, str]:
    """
    Retourne la palette de couleurs pour un thème donné.

    Args:
        theme_name: Nom du thème ("light" ou "dark").

    Returns:
        Dict contenant toutes les couleurs du thème.
    """
    if theme_name not in THEMES:
        theme_name = "light"
    return THEMES[theme_name].copy()


def get_current_theme() -> Dict[str, str]:
    """
    Détecte le thème Windows actuel et retourne la palette correspondante.

    Returns:
        Dict contenant toutes les couleurs du thème actuel.
    """
    theme_name = detect_windows_theme()
    return get_theme_colors(theme_name)


def get_current_theme_name() -> Literal["light", "dark"]:
    """
    Retourne le nom du thème actuel.

    Returns:
        "light" ou "dark".
    """
    return detect_windows_theme()
