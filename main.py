"""Point d'entrée du correcteur orthographique système."""

import sys
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from config import ANTHROPIC_API_KEY, save_api_key
from clipboard import get_selected_text, paste_text, select_pasted_text
from api_client import process_text, APIClientError
from ui import show_error, ask_api_key
from tray import TrayIcon

# Texte affiché pendant le traitement
LOADING_TEXT = "..."

# Message d'aide avec les raccourcis
HELP_MESSAGE = """Ctrl+Alt+C : Corriger
Ctrl+Alt+F : Formater
Ctrl+Alt+R : Reformuler
Ctrl+Alt+P : Rédiger US/Bug/Message
Ctrl+Alt+T : Traduire en anglais
Ctrl+Alt+, : Afficher cette aide"""

# Mapping des virtual key codes vers les actions (plus fiable sur Windows)
# VK codes: C=67, F=70, R=82, P=80, T=84, ,=188
HOTKEY_VK_ACTIONS = {
    67: 'correct',      # C
    70: 'format',       # F
    82: 'reformulate',  # R
    80: 'professional', # P
    84: 'translate',    # T
    188: 'help',        # , (virgule)
}


class TypoApp:
    """Application principale du correcteur orthographique."""

    def __init__(self):
        self.active = True
        self.processing = False
        self.hotkey_listener = None
        self.tray = None
        self.pressed_keys = set()

    def on_hotkey(self, action: str) -> None:
        """
        Gère l'appui sur un raccourci clavier.

        Args:
            action: L'action à effectuer.
        """
        # Action spéciale : aide
        if action == 'help':
            if self.tray:
                self.tray.notify("Typo - Raccourcis", HELP_MESSAGE)
            return

        # Ignorer si désactivé ou déjà en traitement
        if not self.active or self.processing:
            return

        self.processing = True

        try:
            # Récupérer le texte sélectionné
            text = get_selected_text()
            if not text:
                self.processing = False
                return

            # Afficher le texte de chargement (remplace la sélection)
            paste_text(LOADING_TEXT)

            # Appeler l'API Claude
            try:
                corrected = process_text(text, action)
            except APIClientError as e:
                # En cas d'erreur, restaurer le texte original
                select_pasted_text(len(LOADING_TEXT))
                paste_text(text)
                self.processing = False
                return

            # Sélectionner le texte de chargement et le remplacer par le résultat
            select_pasted_text(len(LOADING_TEXT))
            paste_text(corrected)
            self.processing = False

        except Exception:
            self.processing = False

    def on_toggle(self, active: bool) -> None:
        """
        Callback quand l'utilisateur active/désactive via le tray.

        Args:
            active: Nouvel état.
        """
        self.active = active

    def on_quit(self) -> None:
        """Callback quand l'utilisateur quitte via le tray."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        sys.exit(0)

    def on_key_press(self, key) -> None:
        """Callback quand une touche est pressée."""
        self.pressed_keys.add(key)
        self._check_hotkey(key)

    def on_key_release(self, key) -> None:
        """Callback quand une touche est relâchée."""
        self.pressed_keys.discard(key)

    def _check_hotkey(self, key) -> None:
        """Vérifie si un raccourci Ctrl+Alt+X est pressé."""
        # Vérifier si Ctrl et Alt sont pressés
        ctrl_pressed = Key.ctrl_l in self.pressed_keys or Key.ctrl_r in self.pressed_keys
        alt_pressed = Key.alt_l in self.pressed_keys or Key.alt_r in self.pressed_keys or Key.alt_gr in self.pressed_keys

        if not (ctrl_pressed and alt_pressed):
            return

        # Récupérer le virtual key code de la touche
        vk = None
        if isinstance(key, KeyCode):
            vk = getattr(key, 'vk', None)

        if vk and vk in HOTKEY_VK_ACTIONS:
            action = HOTKEY_VK_ACTIONS[vk]
            threading.Thread(
                target=self.on_hotkey,
                args=(action,),
                daemon=True
            ).start()

    def start_hotkey_listener(self) -> None:
        """Démarre le listener de raccourcis clavier."""
        self.hotkey_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.hotkey_listener.start()

    def run(self) -> None:
        """Lance l'application."""
        # Vérifier la clé API, demander si absente
        if not ANTHROPIC_API_KEY:
            api_key = ask_api_key()
            if not api_key:
                sys.exit(0)  # L'utilisateur a annulé
            save_api_key(api_key)

        # Démarrer le listener de raccourcis
        self.start_hotkey_listener()

        # Créer et lancer l'icône tray
        self.tray = TrayIcon(
            on_toggle=self.on_toggle,
            on_quit=self.on_quit
        )

        # Vérifier les mises à jour au démarrage (en arrière-plan)
        def check_updates_on_startup():
            # Attendre 3 secondes après le démarrage avant de vérifier
            import time
            time.sleep(3)
            if self.tray:
                self.tray._check_update()

        threading.Thread(target=check_updates_on_startup, daemon=True).start()

        # L'icône tray bloque ici
        self.tray.run()


def main():
    """Point d'entrée."""
    app = TypoApp()
    app.run()


if __name__ == "__main__":
    main()
