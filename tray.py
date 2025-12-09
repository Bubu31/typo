"""Icône system tray avec menu."""

import pystray
from PIL import Image, ImageDraw, ImageFont
from typing import Callable


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

    # Couleur selon l'état
    color = '#4CAF50' if active else '#9E9E9E'

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

    def _create_menu(self) -> pystray.Menu:
        """Crée le menu contextuel."""
        return pystray.Menu(
            pystray.MenuItem(
                lambda item: "Désactiver" if self.active else "Activer",
                self._toggle,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Raccourcis",
                pystray.Menu(
                    pystray.MenuItem("Ctrl+Alt+C : Corriger", None, enabled=False),
                    pystray.MenuItem("Ctrl+Alt+F : Formater", None, enabled=False),
                    pystray.MenuItem("Ctrl+Alt+R : Reformuler", None, enabled=False),
                    pystray.MenuItem("Ctrl+Alt+P : US/Bug/Message", None, enabled=False),
                    pystray.MenuItem("Ctrl+Alt+T : Traduire EN", None, enabled=False),
                    pystray.MenuItem("Ctrl+Alt+, : Aide", None, enabled=False),
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quitter", self._quit)
        )

    def _toggle(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Bascule l'état actif/inactif."""
        self.active = not self.active
        self.icon.icon = create_icon_image(self.active)
        self.on_toggle(self.active)

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
