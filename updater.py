"""Gestion des mises à jour de l'application."""

import os
import sys
import subprocess
import urllib.request
import json
from typing import Optional, Tuple
from version import __version__

GITHUB_REPO = "Bubu31/typo"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class UpdateInfo:
    """Informations sur une mise à jour disponible."""

    def __init__(self, version: str, download_url: str, release_notes: str):
        self.version = version
        self.download_url = download_url
        self.release_notes = release_notes


def compare_versions(current: str, latest: str) -> bool:
    """
    Compare deux versions au format semver (x.y.z).

    Args:
        current: Version actuelle
        latest: Dernière version disponible

    Returns:
        True si latest > current, False sinon
    """
    def parse_version(v: str) -> Tuple[int, int, int]:
        """Parse une version string en tuple (major, minor, patch)."""
        # Enlever le 'v' au début si présent
        v = v.lstrip('v')
        parts = v.split('.')
        return tuple(int(p) for p in parts[:3])

    try:
        current_parts = parse_version(current)
        latest_parts = parse_version(latest)
        return latest_parts > current_parts
    except (ValueError, IndexError):
        return False


def check_for_updates() -> Optional[UpdateInfo]:
    """
    Vérifie si une nouvelle version est disponible sur GitHub.

    Returns:
        UpdateInfo si une mise à jour est disponible, None sinon
    """
    try:
        # Récupérer les informations de la dernière release
        req = urllib.request.Request(GITHUB_API_URL)
        req.add_header('Accept', 'application/vnd.github.v3+json')

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        latest_version = data['tag_name'].lstrip('v')

        # Vérifier si une mise à jour est disponible
        if not compare_versions(__version__, latest_version):
            return None

        # Trouver l'asset .exe
        download_url = None
        for asset in data.get('assets', []):
            if asset['name'].endswith('.exe'):
                download_url = asset['browser_download_url']
                break

        if not download_url:
            return None

        release_notes = data.get('body', 'Aucune note de version disponible.')

        return UpdateInfo(
            version=latest_version,
            download_url=download_url,
            release_notes=release_notes
        )

    except Exception:
        # En cas d'erreur (pas de connexion, API down, etc.), ne rien faire
        return None


def download_update(update_info: UpdateInfo, progress_callback=None) -> Optional[str]:
    """
    Télécharge la nouvelle version.

    Args:
        update_info: Informations sur la mise à jour
        progress_callback: Fonction appelée avec le pourcentage de progression

    Returns:
        Le chemin du fichier téléchargé, ou None en cas d'erreur
    """
    try:
        # Créer un dossier temporaire pour le téléchargement
        temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), 'typo_update')
        os.makedirs(temp_dir, exist_ok=True)

        temp_file = os.path.join(temp_dir, f'Typo_v{update_info.version}.exe')

        # Télécharger le fichier avec suivi de progression
        def report_progress(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, (downloaded * 100) // total_size)
                progress_callback(percent)

        urllib.request.urlretrieve(
            update_info.download_url,
            temp_file,
            reporthook=report_progress
        )

        return temp_file

    except Exception:
        return None


def install_update(exe_path: str) -> bool:
    """
    Installe la mise à jour en remplaçant l'exécutable actuel.

    Args:
        exe_path: Chemin de la nouvelle version téléchargée

    Returns:
        True si l'installation a réussi, False sinon
    """
    try:
        # Si on est dans un .exe PyInstaller
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable

            # Créer un script batch pour remplacer l'exécutable
            # Le script attend que le processus actuel se termine, puis remplace le fichier
            batch_script = os.path.join(
                os.environ.get('TEMP', '/tmp'),
                'typo_update.bat'
            )

            with open(batch_script, 'w') as f:
                f.write(f'''@echo off
echo Mise à jour de Typo en cours...
timeout /t 2 /nobreak >nul
move /y "{exe_path}" "{current_exe}"
if errorlevel 1 (
    echo Erreur lors de la mise à jour
    pause
    exit /b 1
)
echo Mise à jour terminée ! Redémarrage...
start "" "{current_exe}"
del "%~f0"
''')

            # Lancer le script et quitter l'application
            subprocess.Popen(
                ['cmd', '/c', batch_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return True
        else:
            # En mode développement, on ne peut pas se mettre à jour
            return False

    except Exception:
        return False
