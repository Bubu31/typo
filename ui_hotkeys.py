"""Fenêtre de personnalisation des raccourcis clavier."""

import tkinter as tk
from tkinter import ttk, messagebox
import hotkey_manager
import theme_manager


class HotkeysManagerWindow:
    """Fenêtre de gestion des raccourcis."""

    def __init__(self):
        """Initialise la fenêtre."""
        self.colors = theme_manager.get_current_theme()
        self.hotkeys = {}
        self.modified = False

        self.root = tk.Tk()
        self.root.title("Personnaliser les raccourcis")
        self.root.geometry("700x500")
        self.root.configure(bg=self.colors["bg"])

        # Centrer
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 700) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_hotkeys()

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Info
        tk.Label(
            main_frame,
            text="Cliquez sur 'Modifier' pour changer un raccourci",
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"],
            font=('Segoe UI', 9)
        ).pack(anchor='w', pady=(0, 10))

        # Table
        list_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        list_frame.pack(fill='both', expand=True)

        columns = ('action', 'hotkey', 'edit')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        self.tree.heading('action', text='Action')
        self.tree.heading('hotkey', text='Raccourci actuel')
        self.tree.heading('edit', text='')

        self.tree.column('action', width=300)
        self.tree.column('hotkey', width=200)
        self.tree.column('edit', width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<Double-Button-1>', lambda e: self._edit_hotkey())

        # Warnings
        self.warning_label = tk.Label(
            main_frame,
            text="",
            bg=self.colors["bg"],
            fg="#FF5555",
            font=('Segoe UI', 9)
        )
        self.warning_label.pack(fill='x', pady=(10, 0))

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        btn_frame.pack(fill='x', pady=(10, 0))

        tk.Button(
            btn_frame,
            text="Modifier",
            command=self._edit_hotkey,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left')

        tk.Button(
            btn_frame,
            text="Réinitialiser tout",
            command=self._reset_all,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=(5, 0))

        tk.Button(
            btn_frame,
            text="Annuler",
            command=self._cancel,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='right')

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

    def _load_hotkeys(self):
        """Charge les raccourcis."""
        self.tree.delete(*self.tree.get_children())
        self.hotkeys = hotkey_manager.get_all_hotkeys().copy()

        for action, hotkey_config in self.hotkeys.items():
            label = hotkey_manager.get_action_label(action)
            display = hotkey_manager.format_hotkey_display(hotkey_config)
            self.tree.insert('', 'end', values=(label, display, 'Modifier'), tags=(action,))

        self._check_conflicts()

    def _check_conflicts(self):
        """Vérifie les conflits."""
        conflicts = []
        checked = set()

        for action, hotkey_config in self.hotkeys.items():
            if action in checked:
                continue

            action_conflicts = hotkey_manager.check_conflicts(hotkey_config, exclude_action=action)
            if action_conflicts:
                for other_action in action_conflicts:
                    if other_action not in checked:
                        conflicts.append((action, other_action))
                        checked.add(action)
                        checked.add(other_action)

        if conflicts:
            conflict_text = ", ".join([f"{a1}/{a2}" for a1, a2 in conflicts])
            self.warning_label.config(text=f"⚠ Conflits détectés : {conflict_text}")
        else:
            self.warning_label.config(text="")

        return len(conflicts) == 0

    def _edit_hotkey(self):
        """Édite le raccourci sélectionné."""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        action = item['tags'][0]
        current_hotkey = self.hotkeys[action]

        dialog = HotkeyEditDialog(self.root, action, current_hotkey)
        if dialog.result:
            self.hotkeys[action] = dialog.result
            self.modified = True
            self._load_hotkeys()

    def _reset_all(self):
        """Réinitialise tous les raccourcis."""
        if messagebox.askyesno(
            "Confirmer",
            "Réinitialiser tous les raccourcis aux valeurs par défaut ?"
        ):
            from settings_manager import DEFAULT_CONFIG
            self.hotkeys = DEFAULT_CONFIG["hotkeys"].copy()
            self.modified = True
            self._load_hotkeys()

    def _save(self):
        """Sauvegarde les raccourcis."""
        # Vérifier les conflits
        if not self._check_conflicts():
            if not messagebox.askyesno(
                "Conflits détectés",
                "Des conflits de raccourcis ont été détectés. Enregistrer quand même ?"
            ):
                return

        # Sauvegarder
        import settings_manager
        settings_manager.set("hotkeys", self.hotkeys)

        messagebox.showinfo("Succès", "Raccourcis sauvegardés. Redémarrez l'application pour appliquer les changements.")
        self.root.destroy()

    def _cancel(self):
        """Annule les modifications."""
        if self.modified:
            if messagebox.askyesno("Confirmer", "Annuler les modifications ?"):
                self.root.destroy()
        else:
            self.root.destroy()

    def show(self):
        """Affiche la fenêtre."""
        self.root.mainloop()


class HotkeyEditDialog:
    """Dialog de capture de raccourci."""

    def __init__(self, parent, action: str, current_hotkey: dict):
        """Initialise le dialog."""
        self.action = action
        self.result = None
        self.colors = theme_manager.get_current_theme()
        self.captured_hotkey = current_hotkey.copy()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Modifier le raccourci - {hotkey_manager.get_action_label(action)}")
        self.dialog.geometry("400x250")
        self.dialog.configure(bg=self.colors["bg"])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 250) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.dialog, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        tk.Label(
            main_frame,
            text="Appuyez sur la nouvelle combinaison...",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=('Segoe UI', 10)
        ).pack(pady=(0, 20))

        # Display
        self.display_var = tk.StringVar(value=hotkey_manager.format_hotkey_display(self.captured_hotkey))
        display_label = tk.Label(
            main_frame,
            textvariable=self.display_var,
            bg=self.colors["bg_secondary"],
            fg=self.colors["accent"],
            font=('Segoe UI', 16, 'bold'),
            padx=20,
            pady=20
        )
        display_label.pack(fill='x', pady=(0, 10))

        # Error
        self.error_var = tk.StringVar()
        tk.Label(
            main_frame,
            textvariable=self.error_var,
            bg=self.colors["bg"],
            fg="#FF5555",
            font=('Segoe UI', 9)
        ).pack(pady=(0, 20))

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        btn_frame.pack(fill='x')

        tk.Button(
            btn_frame,
            text="Valider",
            command=self._validate,
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

        # Bind key capture
        self.dialog.bind('<Key>', self._on_key_press)
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.shift_pressed = False

    def _on_key_press(self, event):
        """Capture une touche."""
        # Modifier keys
        if event.keysym in ('Control_L', 'Control_R'):
            self.ctrl_pressed = True
            return
        if event.keysym in ('Alt_L', 'Alt_R'):
            self.alt_pressed = True
            return
        if event.keysym in ('Shift_L', 'Shift_R'):
            self.shift_pressed = True
            return

        # Regular key
        if event.char and event.char.isprintable():
            key_char = event.char.lower()
        elif event.keysym == 'comma':
            key_char = 'comma'
        elif event.keysym == 'period':
            key_char = 'period'
        elif event.keysym == 'space':
            key_char = 'space'
        else:
            return

        # Build hotkey config
        self.captured_hotkey = {
            "ctrl": self.ctrl_pressed,
            "alt": self.alt_pressed,
            "shift": self.shift_pressed,
            "key": key_char
        }

        # Update display
        self.display_var.set(hotkey_manager.format_hotkey_display(self.captured_hotkey))

        # Validate
        is_valid, error = hotkey_manager.validate_hotkey(self.captured_hotkey)
        if not is_valid:
            self.error_var.set(f"⚠ {error}")
        else:
            # Check conflicts
            conflicts = hotkey_manager.check_conflicts(self.captured_hotkey, exclude_action=self.action)
            if conflicts:
                self.error_var.set(f"⚠ Conflit avec : {', '.join(conflicts)}")
            else:
                self.error_var.set("")

    def _validate(self):
        """Valide le raccourci."""
        is_valid, error = hotkey_manager.validate_hotkey(self.captured_hotkey)
        if not is_valid:
            messagebox.showerror("Erreur", error)
            return

        self.result = self.captured_hotkey
        self.dialog.destroy()
