"""Point d'entrée du correcteur orthographique système."""

import sys
import threading
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

import settings_manager
import snippet_manager
import hotkey_manager
from clipboard import get_selected_text, paste_text, select_pasted_text
from api_client import process_text, APIClientError
from ui import show_error, ask_api_key
from tray import TrayIcon

# Texte affiché pendant le traitement
LOADING_TEXT = "..."


class TypoApp:
    """Application principale du correcteur orthographique."""

    def __init__(self):
        self.active = True
        self.processing = False
        self.hotkey_listener = None
        self.tray = None
        self.pressed_keys = set()
        self.hotkey_vk_actions = {}  # Mapping VK code -> action (Ctrl+Alt)
        self.snippet_vk_actions = {}  # Mapping VK code -> action (Ctrl+Shift) pour snippets
        self._build_hotkey_map()

    def _build_hotkey_map(self) -> None:
        """Construit le mapping VK code -> action depuis la configuration."""
        self.hotkey_vk_actions = {}
        self.snippet_vk_actions = {}
        all_hotkeys = hotkey_manager.get_all_hotkeys()

        for action, hotkey_config in all_hotkeys.items():
            vk = hotkey_manager.parse_hotkey(hotkey_config)
            if vk:
                self.hotkey_vk_actions[vk] = action

        # Ajouter les hotkeys pour les snippets (Ctrl+Shift+1 à 9)
        # VK codes: rangée supérieure 49-57, numpad 97-105
        for slot in range(1, 10):
            # Rangée supérieure (1-9 = VK 49-57)
            vk_top = 48 + slot
            self.snippet_vk_actions[vk_top] = f"snippet_{slot}"
            # Numpad (1-9 = VK 97-105)
            vk_numpad = 96 + slot
            self.snippet_vk_actions[vk_numpad] = f"snippet_{slot}"

    def reload_settings(self) -> None:
        """Recharge les paramètres depuis les fichiers JSON."""
        # Recharger config.json
        try:
            new_config = settings_manager.reload_config()
        except Exception as e:
            raise Exception(f"Erreur lecture config.json: {str(e)}")

        # Valider hotkeys (détecter conflits)
        all_hotkeys = hotkey_manager.get_all_hotkeys()
        conflict_pairs = []
        checked = set()

        for action, hotkey_config in all_hotkeys.items():
            if action in checked:
                continue

            conflicts = hotkey_manager.check_conflicts(hotkey_config, exclude_action=action)
            if conflicts:
                for other in conflicts:
                    if other not in checked:
                        conflict_pairs.append((action, other))
                        checked.add(action)
                        checked.add(other)

        # Avertir des conflits (mais continuer)
        if conflict_pairs and self.tray:
            conflict_text = ", ".join([f"{a1}/{a2}" for a1, a2 in conflict_pairs])
            self.tray.notify(
                "Typo - Avertissement",
                f"Conflits de raccourcis : {conflict_text}"
            )

        # Reconstruire la map hotkeys
        self._build_hotkey_map()

    def generate_help_message(self) -> str:
        """Génère le message d'aide avec les raccourcis actuels."""
        lines = []
        all_hotkeys = hotkey_manager.get_all_hotkeys()

        # Filtrer les actions principales (pas les snippets)
        main_actions = ['correct', 'format', 'reformulate', 'professional', 'translate', 'help']

        for action in main_actions:
            if action in all_hotkeys:
                display = hotkey_manager.format_hotkey_display(all_hotkeys[action])
                label = hotkey_manager.get_action_label(action)
                lines.append(f"{display} : {label}")

        return "\n".join(lines)

    def on_hotkey(self, action: str) -> None:
        """
        Gère l'appui sur un raccourci clavier.

        Args:
            action: L'action à effectuer.
        """
        # Action spéciale : aide
        if action == 'help':
            if self.tray:
                help_msg = self.generate_help_message()
                self.tray.notify("Typo - Raccourcis", help_msg)
            return

        # Action snippet : coller directement sans API
        if action.startswith('snippet_'):
            self._handle_snippet(action)
            return

        # Action snippet_search : ouvrir fenêtre de recherche
        if action == 'snippet_search':
            self._open_snippet_search()
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

            # Appeler l'API Claude avec la langue configurée
            try:
                language = settings_manager.get("language", "fr")
                corrected = process_text(text, action, language)
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

    def _handle_snippet(self, action: str) -> None:
        """
        Gère l'insertion d'un snippet.

        Args:
            action: Action snippet (ex: "snippet_1").
        """
        # Extraire le numéro de slot
        try:
            slot = int(action.split('_')[1])
        except (IndexError, ValueError):
            return

        # Récupérer le snippet
        snippet = snippet_manager.get_snippet_by_slot(slot)
        if not snippet:
            return

        # Coller le contenu
        content = snippet.get('content', '')
        if content:
            paste_text(content)

    def _open_snippet_search(self) -> None:
        """Ouvre la fenêtre de recherche de snippets."""
        # Import ici pour éviter circular import
        try:
            from ui_snippets import SnippetSearchWindow
            window = SnippetSearchWindow(on_select=self._on_snippet_selected)
            window.show()
        except ImportError:
            pass  # ui_snippets pas encore créé

    def _on_snippet_selected(self, snippet: dict) -> None:
        """Callback quand un snippet est sélectionné dans la recherche."""
        content = snippet.get('content', '')
        if content:
            paste_text(content)

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
        """Vérifie si un raccourci est pressé."""
        # Vérifier les modificateurs
        ctrl_pressed = Key.ctrl_l in self.pressed_keys or Key.ctrl_r in self.pressed_keys
        alt_pressed = Key.alt_l in self.pressed_keys or Key.alt_r in self.pressed_keys or Key.alt_gr in self.pressed_keys
        shift_pressed = Key.shift_l in self.pressed_keys or Key.shift_r in self.pressed_keys or Key.shift in self.pressed_keys

        # Récupérer le virtual key code de la touche
        vk = None
        if isinstance(key, KeyCode):
            vk = getattr(key, 'vk', None)

        # Vérifier Ctrl+Shift pour les snippets (1-9)
        if ctrl_pressed and shift_pressed and not alt_pressed and vk:
            if vk in self.snippet_vk_actions:
                action = self.snippet_vk_actions[vk]
                threading.Thread(target=self.on_hotkey, args=(action,), daemon=True).start()
                return

        # Vérifier Ctrl+Alt pour les autres actions
        if not (ctrl_pressed and alt_pressed):
            return

        if vk and vk in self.hotkey_vk_actions:
            action = self.hotkey_vk_actions[vk]
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
        # Charger la configuration (migration automatique depuis .env)
        settings_manager.get_config()

        # Vérifier la clé API, demander si absente
        api_key = settings_manager.get_api_key()
        if not api_key:
            api_key = ask_api_key()
            if not api_key:
                sys.exit(0)  # L'utilisateur a annulé
            settings_manager.set_api_key(api_key)

        # Démarrer le listener de raccourcis
        self.start_hotkey_listener()

        # Créer et lancer l'icône tray
        self.tray = TrayIcon(
            on_toggle=self.on_toggle,
            on_quit=self.on_quit,
            on_reload=self.reload_settings
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
