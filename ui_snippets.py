"""Fenêtres de gestion et recherche de snippets."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import snippet_manager
import theme_manager


class SnippetSearchWindow:
    """Fenêtre de recherche rapide de snippets."""

    def __init__(self, on_select: Callable[[dict], None]):
        """
        Initialise la fenêtre de recherche.

        Args:
            on_select: Callback appelé avec le snippet sélectionné.
        """
        self.on_select = on_select
        self.colors = theme_manager.get_current_theme()
        self.filtered_snippets = []

        self.root = tk.Tk()
        self.root.title("Rechercher un snippet")
        self.root.attributes('-topmost', True)
        self.root.geometry("500x400")
        self.root.configure(bg=self.colors["bg"])

        # Centrer
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._bind_keys()
        self._update_results("")

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Barre de recherche
        search_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        search_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            search_frame,
            text="Recherche :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(side='left', padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._update_results(self.search_var.get()))

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10)
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.focus_set()

        # Liste de résultats
        list_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        list_frame.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.listbox = tk.Listbox(
            list_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["bg"],
            font=('Segoe UI', 10),
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Info
        tk.Label(
            main_frame,
            text="Entrée pour coller • Échap pour annuler",
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"],
            font=('Segoe UI', 8)
        ).pack(pady=(5, 0))

    def _bind_keys(self):
        """Configure les raccourcis."""
        self.root.bind('<Return>', lambda e: self._select())
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.listbox.bind('<Double-Button-1>', lambda e: self._select())

    def _update_results(self, query: str):
        """Met à jour la liste de résultats."""
        self.listbox.delete(0, tk.END)
        self.filtered_snippets = snippet_manager.search_snippets(query)

        for snippet in self.filtered_snippets:
            label = snippet.get('label', 'Sans nom')
            self.listbox.insert(tk.END, label)

        if self.filtered_snippets:
            self.listbox.select_set(0)

    def _select(self):
        """Sélectionne le snippet actuel."""
        selection = self.listbox.curselection()
        if selection and self.filtered_snippets:
            snippet = self.filtered_snippets[selection[0]]
            self.root.destroy()
            self.on_select(snippet)

    def show(self):
        """Affiche la fenêtre."""
        self.root.mainloop()


class SnippetsManagerWindow:
    """Fenêtre de gestion des snippets."""

    def __init__(self):
        """Initialise la fenêtre."""
        self.colors = theme_manager.get_current_theme()
        self.snippets = []

        self.root = tk.Tk()
        self.root.title("Gestion des snippets")
        self.root.geometry("700x500")
        self.root.configure(bg=self.colors["bg"])

        # Centrer
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 700) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_snippets()

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Liste
        list_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        list_frame.pack(fill='both', expand=True)

        # Treeview
        columns = ('label', 'hotkey', 'actions')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        self.tree.heading('label', text='Label')
        self.tree.heading('hotkey', text='Raccourci')
        self.tree.heading('actions', text='')

        self.tree.column('label', width=400)
        self.tree.column('hotkey', width=150)
        self.tree.column('actions', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        btn_frame.pack(fill='x', pady=(10, 0))

        tk.Button(
            btn_frame,
            text="+ Nouveau snippet",
            command=self._new_snippet,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left')

        tk.Button(
            btn_frame,
            text="Modifier",
            command=self._edit_snippet,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=(5, 0))

        tk.Button(
            btn_frame,
            text="Supprimer",
            command=self._delete_snippet,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=(5, 0))

        tk.Button(
            btn_frame,
            text="Fermer",
            command=self.root.destroy,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='right')

        self.tree.bind('<Double-Button-1>', lambda e: self._edit_snippet())

    def _load_snippets(self):
        """Charge les snippets."""
        self.tree.delete(*self.tree.get_children())
        self.snippets = snippet_manager.get_all_snippets()

        for snippet in self.snippets:
            label = snippet.get('label', 'Sans nom')
            slot = snippet.get('hotkey_slot')
            hotkey = f"Ctrl+Shift+{slot}" if slot else "(aucun)"

            self.tree.insert('', 'end', values=(label, hotkey, ''), tags=(snippet['id'],))

    def _new_snippet(self):
        """Crée un nouveau snippet."""
        SnippetEditDialog(self.root, None, on_save=self._load_snippets)

    def _edit_snippet(self):
        """Édite le snippet sélectionné."""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        snippet_id = item['tags'][0]
        snippet = snippet_manager.get_snippet(snippet_id)

        if snippet:
            SnippetEditDialog(self.root, snippet, on_save=self._load_snippets)

    def _delete_snippet(self):
        """Supprime le snippet sélectionné."""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        snippet_id = item['tags'][0]
        snippet = snippet_manager.get_snippet(snippet_id)

        if snippet and messagebox.askyesno(
            "Confirmer",
            f"Supprimer le snippet '{snippet['label']}' ?"
        ):
            snippet_manager.delete_snippet(snippet_id)
            self._load_snippets()

    def show(self):
        """Affiche la fenêtre."""
        self.root.mainloop()


class SnippetEditDialog:
    """Dialog d'édition de snippet."""

    def __init__(self, parent, snippet: Optional[dict], on_save: Optional[Callable[[], None]] = None):
        """
        Initialise le dialog.

        Args:
            parent: Fenêtre parente.
            snippet: Snippet à éditer, ou None pour nouveau.
            on_save: Callback appelé après sauvegarde réussie.
        """
        self.snippet = snippet
        self.result = False
        self.on_save = on_save
        self.colors = theme_manager.get_current_theme()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier le snippet" if snippet else "Nouveau snippet")
        self.dialog.geometry("600x400")
        self.dialog.configure(bg=self.colors["bg"])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.dialog, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Label
        tk.Label(
            main_frame,
            text="Label :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(anchor='w')

        self.label_entry = tk.Entry(
            main_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10)
        )
        self.label_entry.pack(fill='x', pady=(0, 10))

        if self.snippet:
            self.label_entry.insert(0, self.snippet.get('label', ''))

        # Contenu
        tk.Label(
            main_frame,
            text="Contenu :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(anchor='w')

        text_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        text_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.content_text = tk.Text(
            text_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.content_text.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.content_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.content_text.config(yscrollcommand=scrollbar.set)

        if self.snippet:
            self.content_text.insert('1.0', self.snippet.get('content', ''))

        # Hotkey slot
        hotkey_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        hotkey_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            hotkey_frame,
            text="Raccourci rapide :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(side='left', padx=(0, 5))

        self.slot_var = tk.StringVar(value="Aucun")
        slot_values = ["Aucun"] + [f"Ctrl+Shift+{i} (slot {i})" for i in range(1, 10)]

        if self.snippet and self.snippet.get('hotkey_slot'):
            slot = self.snippet['hotkey_slot']
            self.slot_var.set(f"Ctrl+Shift+{slot} (slot {slot})")

        slot_menu = ttk.Combobox(
            hotkey_frame,
            textvariable=self.slot_var,
            values=slot_values,
            state='readonly',
            width=25
        )
        slot_menu.pack(side='left')

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        btn_frame.pack(fill='x')

        tk.Button(
            btn_frame,
            text="Enregistrer",
            command=self._save,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='right', padx=(5, 0))

        tk.Button(
            btn_frame,
            text="Annuler",
            command=self.dialog.destroy,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='right')

    def _save(self):
        """Sauvegarde le snippet."""
        label = self.label_entry.get().strip()
        content = self.content_text.get('1.0', 'end-1c').strip()

        if not label or not content:
            messagebox.showerror("Erreur", "Le label et le contenu sont obligatoires")
            return

        # Parser le slot
        slot_text = self.slot_var.get()
        slot = None
        if "slot" in slot_text:
            try:
                slot = int(slot_text.split("slot")[1].strip().rstrip(")"))
            except:
                pass

        # Sauvegarder
        snippet_id = self.snippet['id'] if self.snippet else None
        snippet_manager.save_snippet(label, content, slot, snippet_id)

        self.result = True
        self.dialog.destroy()

        # Appeler le callback si défini
        if self.on_save:
            self.on_save()
