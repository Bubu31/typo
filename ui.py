"""Interface utilisateur : popup de prévisualisation."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from config import ACTION_LABELS


class PreviewPopup:
    """Popup de prévisualisation du texte corrigé."""

    def __init__(
        self,
        original: str,
        corrected: str,
        action: str,
        on_accept: Callable[[str], None],
        on_cancel: Callable[[], None]
    ):
        """
        Initialise le popup.

        Args:
            original: Texte original.
            corrected: Texte corrigé.
            action: Action effectuée (pour le titre).
            on_accept: Callback appelé avec le texte final si l'utilisateur valide.
            on_cancel: Callback appelé si l'utilisateur annule.
        """
        self.on_accept = on_accept
        self.on_cancel = on_cancel

        self.root = tk.Tk()
        self.root.title(f"Typo - {ACTION_LABELS.get(action, action)}")
        self.root.attributes('-topmost', True)
        self.root.geometry("650x450")
        self.root.minsize(400, 300)

        # Centrer la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 650) // 2
        y = (self.root.winfo_screenheight() - 450) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets(original, corrected)
        self._bind_keys()

    def _create_widgets(self, original: str, corrected: str) -> None:
        """Crée les widgets de l'interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Section texte original
        ttk.Label(
            main_frame,
            text="Original :",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w')

        original_frame = ttk.Frame(main_frame)
        original_frame.pack(fill='x', pady=(5, 10))

        original_text = tk.Text(
            original_frame,
            height=5,
            wrap=tk.WORD,
            bg='#f5f5f5',
            relief='flat',
            font=('Segoe UI', 10)
        )
        original_text.insert('1.0', original)
        original_text.config(state='disabled')
        original_text.pack(side='left', fill='x', expand=True)

        original_scroll = ttk.Scrollbar(
            original_frame,
            orient='vertical',
            command=original_text.yview
        )
        original_scroll.pack(side='right', fill='y')
        original_text.config(yscrollcommand=original_scroll.set)

        # Section texte corrigé
        ttk.Label(
            main_frame,
            text="Corrigé (modifiable) :",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w')

        corrected_frame = ttk.Frame(main_frame)
        corrected_frame.pack(fill='both', expand=True, pady=(5, 10))

        self.corrected_text = tk.Text(
            corrected_frame,
            wrap=tk.WORD,
            relief='flat',
            font=('Segoe UI', 10)
        )
        self.corrected_text.insert('1.0', corrected)
        self.corrected_text.pack(side='left', fill='both', expand=True)

        corrected_scroll = ttk.Scrollbar(
            corrected_frame,
            orient='vertical',
            command=self.corrected_text.yview
        )
        corrected_scroll.pack(side='right', fill='y')
        self.corrected_text.config(yscrollcommand=corrected_scroll.set)

        # Focus sur le texte corrigé
        self.corrected_text.focus_set()

        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(5, 0))

        ttk.Button(
            btn_frame,
            text="Appliquer (Ctrl+Entrée)",
            command=self._accept
        ).pack(side='right', padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Annuler (Échap)",
            command=self._cancel
        ).pack(side='right')

    def _bind_keys(self) -> None:
        """Configure les raccourcis clavier."""
        self.root.bind('<Control-Return>', lambda e: self._accept())
        self.root.bind('<Escape>', lambda e: self._cancel())
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)

    def _accept(self) -> None:
        """Valide et ferme le popup."""
        text = self.corrected_text.get('1.0', 'end-1c')
        self.root.destroy()
        self.on_accept(text)

    def _cancel(self) -> None:
        """Annule et ferme le popup."""
        self.root.destroy()
        self.on_cancel()

    def show(self) -> None:
        """Affiche le popup."""
        self.root.mainloop()


def show_error(title: str, message: str) -> None:
    """
    Affiche une boîte de dialogue d'erreur.

    Args:
        title: Titre de la boîte de dialogue.
        message: Message d'erreur.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showerror(title, message)
    root.destroy()


def show_info(title: str, message: str) -> None:
    """
    Affiche une boîte de dialogue d'information.

    Args:
        title: Titre de la boîte de dialogue.
        message: Message d'information.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showinfo(title, message)
    root.destroy()


def ask_api_key() -> str | None:
    """
    Affiche une fenêtre pour demander la clé API.

    Returns:
        La clé API saisie, ou None si annulé.
    """
    result = [None]

    root = tk.Tk()
    root.title("Typo - Configuration")
    root.attributes('-topmost', True)
    root.geometry("500x200")
    root.resizable(False, False)

    # Centrer la fenêtre
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 500) // 2
    y = (root.winfo_screenheight() - 200) // 2
    root.geometry(f"+{x}+{y}")

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill='both', expand=True)

    ttk.Label(
        main_frame,
        text="Bienvenue dans Typo !",
        font=('Segoe UI', 12, 'bold')
    ).pack(anchor='w')

    ttk.Label(
        main_frame,
        text="Entrez votre clé API Anthropic pour commencer :",
        font=('Segoe UI', 10)
    ).pack(anchor='w', pady=(10, 5))

    entry = ttk.Entry(main_frame, width=60, font=('Segoe UI', 10))
    entry.pack(fill='x', pady=(0, 5))
    entry.focus_set()

    ttk.Label(
        main_frame,
        text="(Obtenez votre clé sur console.anthropic.com)",
        font=('Segoe UI', 8),
        foreground='gray'
    ).pack(anchor='w')

    def on_save():
        api_key = entry.get().strip()
        if api_key:
            result[0] = api_key
            root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill='x', pady=(20, 0))

    ttk.Button(btn_frame, text="Enregistrer", command=on_save).pack(side='right', padx=(5, 0))
    ttk.Button(btn_frame, text="Annuler", command=on_cancel).pack(side='right')

    root.bind('<Return>', lambda e: on_save())
    root.bind('<Escape>', lambda e: on_cancel())
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    root.mainloop()

    return result[0]
