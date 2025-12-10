"""Icône system tray avec menu."""

import pystray
from PIL import Image, ImageDraw, ImageFont
from typing import Callable
import threading

from startup import is_startup_enabled, toggle_startup
from updater import check_for_updates, download_update, install_update
from version import __version__
import theme_manager
import settings_manager
import hotkey_manager
import snippet_manager
import translations
import usage_tracker


def create_icon_image(active: bool = True) -> Image.Image:
    """
    Crée une image pour l'icône tray.

    Args:
        active: Si True, icône verte (actif). Si False, icône grise (inactif).

    Returns:
        Image PIL pour l'icône.
    """
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Récupérer les couleurs du thème
    colors = theme_manager.get_current_theme()
    color = colors["tray_icon_color"] if active else colors["tray_icon_inactive"]

    # Dessiner un cercle
    margin = 4
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=color
    )

    # Dessiner la lettre "T"
    try:
        font = ImageFont.truetype("segoeui.ttf", 36)
    except Exception:
        font = ImageFont.load_default()

    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 4
    draw.text((x, y), text, fill='white', font=font)

    return image


class TrayIcon:
    """Gestionnaire de l'icône system tray."""

    def __init__(
        self,
        on_toggle: Callable[[bool], None],
        on_quit: Callable[[], None]
    ):
        """
        Initialise l'icône tray.

        Args:
            on_toggle: Callback appelé quand l'utilisateur active/désactive.
            on_quit: Callback appelé quand l'utilisateur quitte.
        """
        self.active = True
        self.on_toggle = on_toggle
        self.on_quit = on_quit
        self.icon = None
        self.startup_enabled = is_startup_enabled()
        self.checking_update = False

    def _create_menu(self) -> pystray.Menu:
        """Crée le menu contextuel."""
        # Récupérer les hotkeys et snippets actuels
        all_hotkeys = hotkey_manager.get_all_hotkeys()
        snippets_by_hotkey = snippet_manager.get_snippets_by_hotkey()
        current_language = settings_manager.get("language", "fr")

        # Construire sous-menu Raccourcis (dynamique)
        shortcut_items = []
        main_actions = ['correct', 'format', 'reformulate', 'professional', 'translate', 'help']
        for action in main_actions:
            if action in all_hotkeys:
                display = hotkey_manager.format_hotkey_display(all_hotkeys[action])
                label = hotkey_manager.get_action_label(action)
                shortcut_items.append(
                    pystray.MenuItem(f"{display} : {label}", None, enabled=False)
                )

        # Construire sous-menu Snippets
        snippet_items = []
        for slot in range(1, 10):
            if slot in snippets_by_hotkey:
                snippet = snippets_by_hotkey[slot]
                label = snippet.get('label', f'Snippet {slot}')
                shortcut_items_text = f"Ctrl+Alt+{slot}"
                snippet_items.append(
                    pystray.MenuItem(
                        f"{slot}. {label} ({shortcut_items_text})",
                        lambda _, s=snippet: self._paste_snippet(s)
                    )
                )

        if snippet_items:
            snippet_items.append(pystray.Menu.SEPARATOR)

        snippet_items.extend([
            pystray.MenuItem("Rechercher...", self._open_snippet_search),
            pystray.MenuItem("Gérer les snippets...", self._open_snippets_manager)
        ])

        # Construire sous-menu Langue
        language_items = []
        for lang_code, lang_name in translations.get_supported_languages():
            is_current = (lang_code == current_language)
            language_items.append(
                pystray.MenuItem(
                    lambda item, name=lang_name: f"● {name}" if is_current else f"  {name}",
                    lambda _, code=lang_code: self._change_language(code),
                    checked=lambda item, code=lang_code: code == settings_manager.get("language", "fr")
                )
            )

        # Menu principal
        return pystray.Menu(
            pystray.MenuItem(
                lambda item: "Désactiver" if self.active else "Activer",
                self._toggle,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Raccourcis", pystray.Menu(*shortcut_items)),
            pystray.MenuItem("Snippets", pystray.Menu(*snippet_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Langue / Language", pystray.Menu(*language_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Paramètres",
                pystray.Menu(
                    pystray.MenuItem("Personnaliser les raccourcis...", self._open_hotkeys_manager),
                    pystray.MenuItem("Gérer les prompts...", self._open_prompts_manager),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        lambda item: f"Utilisation ce mois : {usage_tracker.format_usage_display()}",
                        None,
                        enabled=False
                    ),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        lambda item: "✓ Démarrer avec Windows" if self.startup_enabled else "  Démarrer avec Windows",
                        self._toggle_startup
                    )
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Version {__version__}", None, enabled=False),
            pystray.MenuItem("Vérifier les mises à jour", self._check_update),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self._quit)
        )

    def _toggle(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Bascule l'état actif/inactif."""
        self.active = not self.active
        self.icon.icon = create_icon_image(self.active)
        self.on_toggle(self.active)

    def _toggle_startup(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Bascule le démarrage automatique avec Windows."""
        self.startup_enabled = toggle_startup()
        status = "activé" if self.startup_enabled else "désactivé"
        self.notify("Typo", f"Démarrage avec Windows {status}")

    def _change_language(self, language: str) -> None:
        """Change la langue de l'application."""
        settings_manager.set("language", language)
        lang_name = dict(translations.get_supported_languages()).get(language, language)
        self.notify("Typo", f"Langue changée : {lang_name}")

    def _paste_snippet(self, snippet: dict) -> None:
        """Colle un snippet depuis le menu."""
        from clipboard import paste_text
        content = snippet.get('content', '')
        if content:
            paste_text(content)

    def _open_snippet_search(self, icon: pystray.Icon = None, item: pystray.MenuItem = None) -> None:
        """Ouvre la fenêtre de recherche de snippets."""
        try:
            from ui_snippets import SnippetSearchWindow
            from clipboard import paste_text

            def on_select(snippet):
                content = snippet.get('content', '')
                if content:
                    paste_text(content)

            window = SnippetSearchWindow(on_select=on_select)
            window.show()
        except ImportError:
            self.notify("Typo", "Fonctionnalité pas encore disponible")

    def _open_snippets_manager(self, icon: pystray.Icon = None, item: pystray.MenuItem = None) -> None:
        """Ouvre la fenêtre de gestion des snippets."""
        try:
            from ui_snippets import SnippetsManagerWindow
            window = SnippetsManagerWindow()
            window.show()
        except ImportError:
            self.notify("Typo", "Fonctionnalité pas encore disponible")

    def _open_prompts_manager(self, icon: pystray.Icon = None, item: pystray.MenuItem = None) -> None:
        """Ouvre la fenêtre de gestion des prompts."""
        try:
            from ui_prompts import PromptsManagerWindow
            window = PromptsManagerWindow()
            window.show()
        except ImportError:
            self.notify("Typo", "Fonctionnalité pas encore disponible")

    def _open_hotkeys_manager(self, icon: pystray.Icon = None, item: pystray.MenuItem = None) -> None:
        """Ouvre la fenêtre de gestion des raccourcis."""
        try:
            from ui_hotkeys import HotkeysManagerWindow
            window = HotkeysManagerWindow()
            window.show()
        except ImportError:
            self.notify("Typo", "Fonctionnalité pas encore disponible")

    def _check_update(self, icon: pystray.Icon = None, item: pystray.MenuItem = None) -> None:
        """Vérifie les mises à jour (en thread pour ne pas bloquer l'UI)."""
        if self.checking_update:
            return

        def check():
            self.checking_update = True
            self.notify("Typo", "Vérification des mises à jour...")

            update_info = check_for_updates()

            if update_info is None:
                self.notify("Typo", f"Vous utilisez la dernière version (v{__version__})")
                self.checking_update = False
                return

            # Proposer le téléchargement
            self.notify(
                "Typo - Mise à jour disponible",
                f"Version {update_info.version} disponible\nTéléchargement en cours..."
            )

            # Télécharger
            def progress(percent):
                if percent % 25 == 0:  # Notifier tous les 25%
                    self.notify("Typo", f"Téléchargement : {percent}%")

            exe_path = download_update(update_info, progress)

            if exe_path is None:
                self.notify("Typo - Erreur", "Échec du téléchargement")
                self.checking_update = False
                return

            # Installer
            self.notify("Typo", "Installation de la mise à jour...")
            success = install_update(exe_path)

            if success:
                self.notify(
                    "Typo",
                    "Mise à jour installée ! L'application va redémarrer..."
                )
                # L'application va redémarrer automatiquement
                self.icon.stop()
                self.on_quit()
            else:
                self.notify("Typo - Erreur", "Échec de l'installation")
                self.checking_update = False

        threading.Thread(target=check, daemon=True).start()

    def _quit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Quitte l'application."""
        self.icon.stop()
        self.on_quit()

    def run(self) -> None:
        """Lance l'icône tray (bloquant)."""
        self.icon = pystray.Icon(
            name="typo",
            icon=create_icon_image(True),
            title="Typo - Correcteur orthographique",
            menu=self._create_menu()
        )
        self.icon.run()

    def stop(self) -> None:
        """Arrête l'icône tray."""
        if self.icon:
            self.icon.stop()

    def is_active(self) -> bool:
        """Retourne l'état actif/inactif."""
        return self.active

    def notify(self, title: str, message: str) -> None:
        """
        Affiche une notification système.

        Args:
            title: Titre de la notification.
            message: Message de la notification.
        """
        if self.icon:
            self.icon.notify(message, title)
