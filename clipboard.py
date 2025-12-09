"""Gestion du clipboard et simulation clavier."""

import time
import pyperclip
from pynput.keyboard import Controller, Key

from config import CLIPBOARD_DELAY, PASTE_DELAY

keyboard_controller = Controller()


def get_selected_text() -> str | None:
    """
    Récupère le texte sélectionné en simulant Ctrl+C.

    Returns:
        Le texte sélectionné, ou None si rien n'est sélectionné.
    """
    # Attendre que les touches du raccourci soient relâchées
    time.sleep(0.2)

    # S'assurer que toutes les touches modificatrices sont relâchées
    keyboard_controller.release(Key.ctrl)
    keyboard_controller.release(Key.ctrl_l)
    keyboard_controller.release(Key.ctrl_r)
    keyboard_controller.release(Key.alt)
    keyboard_controller.release(Key.alt_l)
    keyboard_controller.release(Key.alt_r)
    keyboard_controller.release(Key.alt_gr)
    time.sleep(0.1)

    # Vider le clipboard avant de copier pour éviter les faux négatifs
    try:
        pyperclip.copy('')
    except Exception:
        pass

    # Simuler Ctrl+C
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('c')
    keyboard_controller.release('c')
    keyboard_controller.release(Key.ctrl)

    # Attendre que le clipboard soit mis à jour
    time.sleep(CLIPBOARD_DELAY)

    # Récupérer le nouveau contenu
    try:
        new_clipboard = pyperclip.paste()
    except Exception:
        return None

    # Vérifier si quelque chose a été copié
    if not new_clipboard or not new_clipboard.strip():
        return None

    return new_clipboard


def paste_text(text: str) -> None:
    """
    Colle le texte en simulant Ctrl+V.

    Args:
        text: Le texte à coller.
    """
    # Copier le texte dans le clipboard
    pyperclip.copy(text)

    # Petit délai pour que le focus revienne à l'application
    time.sleep(PASTE_DELAY)

    # Simuler Ctrl+V
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press('v')
    keyboard_controller.release('v')
    keyboard_controller.release(Key.ctrl)

    # Petit délai après le collage
    time.sleep(PASTE_DELAY)


def select_pasted_text(length: int) -> None:
    """
    Sélectionne le texte qui vient d'être collé en faisant Shift+Left.

    Args:
        length: Nombre de caractères à sélectionner.
    """
    time.sleep(0.05)
    keyboard_controller.press(Key.shift)
    for _ in range(length):
        keyboard_controller.press(Key.left)
        keyboard_controller.release(Key.left)
    keyboard_controller.release(Key.shift)
    time.sleep(0.05)
