"""Gestion du démarrage automatique avec Windows."""

import sys
import winreg
from pathlib import Path


APP_NAME = "Typo"
REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_executable_path() -> str:
    """Retourne le chemin de l'exécutable ou du script Python."""
    if getattr(sys, 'frozen', False):
        # Exécutable PyInstaller
        return sys.executable
    else:
        # Script Python - utilise pythonw pour éviter la console
        python_exe = sys.executable
        script_path = Path(__file__).parent / "main.py"
        return f'"{python_exe}" "{script_path}"'


def is_startup_enabled() -> bool:
    """Vérifie si l'application est configurée pour démarrer avec Windows."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except WindowsError:
        return False


def enable_startup() -> bool:
    """Active le démarrage automatique avec Windows."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            exe_path = get_executable_path()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            return True
        finally:
            winreg.CloseKey(key)
    except WindowsError:
        return False


def disable_startup() -> bool:
    """Désactive le démarrage automatique avec Windows."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRY_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, APP_NAME)
            return True
        except FileNotFoundError:
            # Déjà désactivé
            return True
        finally:
            winreg.CloseKey(key)
    except WindowsError:
        return False


def toggle_startup() -> bool:
    """Bascule l'état du démarrage automatique. Retourne le nouvel état."""
    if is_startup_enabled():
        disable_startup()
        return False
    else:
        enable_startup()
        return True
