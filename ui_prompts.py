"""Fenêtre de gestion des prompts personnalisés."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import prompt_manager
import theme_manager
from config import PROMPTS as DEFAULT_PROMPTS


class PromptsManagerWindow:
    """Fenêtre de gestion des prompts."""

    def __init__(self):
        """Initialise la fenêtre."""
        self.colors = theme_manager.get_current_theme()
        self.current_selection = None

        self.root = tk.Tk()
        self.root.title("Gestion des prompts")
        self.root.geometry("900x600")
        self.root.configure(bg=self.colors["bg"])

        # Centrer
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 900) // 2
        y = (self.root.winfo_screenheight() - 600) // 2
        self.root.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._load_prompts()

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)

        # Layout : Liste gauche + Éditeur droite
        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg=self.colors["bg"])
        paned.pack(fill='both', expand=True)

        # Panel gauche : Liste des prompts
        left_panel = tk.Frame(paned, bg=self.colors["bg"], width=300)
        paned.add(left_panel)

        tk.Label(
            left_panel,
            text="PROMPTS",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))

        list_frame = tk.Frame(left_panel, bg=self.colors["bg"])
        list_frame.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.prompts_listbox = tk.Listbox(
            list_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectbackground=self.colors["accent"],
            selectforeground=self.colors["bg"],
            font=('Segoe UI', 10),
            yscrollcommand=scrollbar.set
        )
        self.prompts_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.prompts_listbox.yview)

        self.prompts_listbox.bind('<<ListboxSelect>>', self._on_select)

        # Bouton nouveau
        tk.Button(
            left_panel,
            text="+ Nouveau prompt custom",
            command=self._new_prompt,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=10,
            pady=5
        ).pack(fill='x', pady=(10, 0))

        # Panel droit : Éditeur
        right_panel = tk.Frame(paned, bg=self.colors["bg"])
        paned.add(right_panel)

        # ID / Label
        form_frame = tk.Frame(right_panel, bg=self.colors["bg"])
        form_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            form_frame,
            text="ID :",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            width=10,
            anchor='w'
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(
            form_frame,
            textvariable=self.id_var,
            bg=self.colors["bg_secondary"],
            fg=self.colors["fg"],
            state='readonly',
            font=('Segoe UI', 10)
        )
        self.id_entry.grid(row=0, column=1, sticky='ew', pady=5)

        tk.Label(
            form_frame,
            text="Label :",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            width=10,
            anchor='w'
        ).grid(row=1, column=0, sticky='w', pady=5)

        self.label_entry = tk.Entry(
            form_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10)
        )
        self.label_entry.grid(row=1, column=1, sticky='ew', pady=5)

        form_frame.columnconfigure(1, weight=1)

        # Prompt
        tk.Label(
            right_panel,
            text="Prompt (doit contenir {text}) :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(anchor='w')

        text_frame = tk.Frame(right_panel, bg=self.colors["bg"])
        text_frame.pack(fill='both', expand=True, pady=(5, 10))

        self.prompt_text = tk.Text(
            text_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10),
            wrap=tk.WORD
        )
        self.prompt_text.pack(side='left', fill='both', expand=True)

        text_scrollbar = ttk.Scrollbar(text_frame, command=self.prompt_text.yview)
        text_scrollbar.pack(side='right', fill='y')
        self.prompt_text.config(yscrollcommand=text_scrollbar.set)

        # Boutons
        btn_frame = tk.Frame(right_panel, bg=self.colors["bg"])
        btn_frame.pack(fill='x')

        self.save_btn = tk.Button(
            btn_frame,
            text="Enregistrer",
            command=self._save,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        )
        self.save_btn.pack(side='right', padx=(5, 0))

        self.reset_btn = tk.Button(
            btn_frame,
            text="Réinitialiser",
            command=self._reset,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.reset_btn.pack(side='right', padx=(5, 0))

        self.delete_btn = tk.Button(
            btn_frame,
            text="Supprimer",
            command=self._delete,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.delete_btn.pack(side='right', padx=(5, 0))

        tk.Button(
            btn_frame,
            text="Fermer",
            command=self.root.destroy,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left')

    def _load_prompts(self):
        """Charge la liste des prompts."""
        self.prompts_listbox.delete(0, tk.END)

        # Prompts par défaut
        self.prompts_listbox.insert(tk.END, "--- PROMPTS PAR DÉFAUT ---")
        self.prompts_listbox.itemconfig(tk.END, {'bg': self.colors["bg_secondary"]})

        for action in DEFAULT_PROMPTS.keys():
            label = prompt_manager.get_action_label(action)
            has_override = prompt_manager.has_override(action)
            prefix = "✓ " if has_override else "  "
            self.prompts_listbox.insert(tk.END, f"{prefix}{label}")

        # Prompts custom
        custom_prompts = prompt_manager.get_custom_prompts()
        if custom_prompts:
            self.prompts_listbox.insert(tk.END, "")
            self.prompts_listbox.insert(tk.END, "--- PROMPTS CUSTOM ---")
            self.prompts_listbox.itemconfig(tk.END, {'bg': self.colors["bg_secondary"]})

            for action_id, data in custom_prompts.items():
                enabled = data.get('enabled', True)
                prefix = "✓ " if enabled else "✗ "
                self.prompts_listbox.insert(tk.END, f"{prefix}{data['label']}")

    def _on_select(self, event):
        """Gère la sélection d'un prompt."""
        selection = self.prompts_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        text = self.prompts_listbox.get(idx)

        # Ignorer les séparateurs
        if "---" in text or not text.strip():
            return

        # Déterminer le type (default ou custom)
        default_actions = list(DEFAULT_PROMPTS.keys())
        custom_prompts = prompt_manager.get_custom_prompts()

        # Calculer l'index réel
        real_idx = idx - 1  # Skip header

        if real_idx < len(default_actions):
            # Prompt par défaut
            action = default_actions[real_idx]
            self._load_default_prompt(action)
        else:
            # Prompt custom
            custom_idx = real_idx - len(default_actions) - 2  # Skip default + header + separator
            custom_actions = list(custom_prompts.keys())
            if 0 <= custom_idx < len(custom_actions):
                action_id = custom_actions[custom_idx]
                self._load_custom_prompt(action_id, custom_prompts[action_id])

    def _load_default_prompt(self, action: str):
        """Charge un prompt par défaut."""
        self.current_selection = ('default', action)

        self.id_var.set(action)
        self.label_entry.delete(0, tk.END)
        self.label_entry.insert(0, prompt_manager.get_action_label(action))
        self.label_entry.config(state='readonly')

        # Charger le prompt (override ou default)
        prompt = prompt_manager.get_prompt(action)
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', prompt or "")

        # Activer reset si override
        has_override = prompt_manager.has_override(action)
        self.reset_btn.config(state='normal' if has_override else 'disabled')
        self.delete_btn.config(state='disabled')
        self.save_btn.config(state='normal')

    def _load_custom_prompt(self, action_id: str, data: dict):
        """Charge un prompt custom."""
        self.current_selection = ('custom', action_id)

        self.id_var.set(action_id)
        self.label_entry.delete(0, tk.END)
        self.label_entry.insert(0, data.get('label', ''))
        self.label_entry.config(state='normal')

        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', data.get('prompt', ''))

        self.reset_btn.config(state='disabled')
        self.delete_btn.config(state='normal')
        self.save_btn.config(state='normal')

    def _save(self):
        """Sauvegarde le prompt actuel."""
        if not self.current_selection:
            return

        prompt_type, action_id = self.current_selection
        label = self.label_entry.get().strip()
        prompt = self.prompt_text.get('1.0', 'end-1c').strip()

        if not prompt:
            messagebox.showerror("Erreur", "Le prompt ne peut pas être vide")
            return

        if "{text}" not in prompt:
            messagebox.showerror("Erreur", "Le prompt doit contenir le placeholder {text}")
            return

        if prompt_type == 'default':
            # Override d'un prompt par défaut
            prompt_manager.save_override(action_id, prompt)
            messagebox.showinfo("Succès", "Prompt par défaut overridé")
        else:
            # Custom prompt
            if not label:
                messagebox.showerror("Erreur", "Le label est obligatoire")
                return

            prompt_manager.save_custom_prompt(action_id, label, prompt)
            messagebox.showinfo("Succès", "Prompt custom sauvegardé")

        self._load_prompts()

    def _reset(self):
        """Réinitialise un override."""
        if not self.current_selection:
            return

        prompt_type, action_id = self.current_selection
        if prompt_type != 'default':
            return

        if messagebox.askyesno("Confirmer", "Réinitialiser ce prompt aux valeurs par défaut ?"):
            prompt_manager.reset_to_default(action_id)
            self._load_prompts()
            self._load_default_prompt(action_id)

    def _delete(self):
        """Supprime un prompt custom."""
        if not self.current_selection:
            return

        prompt_type, action_id = self.current_selection
        if prompt_type != 'custom':
            return

        if messagebox.askyesno("Confirmer", "Supprimer ce prompt custom ?"):
            prompt_manager.delete_custom_prompt(action_id)
            self._load_prompts()
            self.current_selection = None
            self.id_var.set("")
            self.label_entry.delete(0, tk.END)
            self.prompt_text.delete('1.0', tk.END)

    def _new_prompt(self):
        """Crée un nouveau prompt custom."""
        dialog = NewPromptDialog(self.root)
        if dialog.result:
            self._load_prompts()

    def show(self):
        """Affiche la fenêtre."""
        self.root.mainloop()


class NewPromptDialog:
    """Dialog pour créer un nouveau prompt custom."""

    def __init__(self, parent):
        """Initialise le dialog."""
        self.result = False
        self.colors = theme_manager.get_current_theme()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau prompt custom")
        self.dialog.geometry("500x200")
        self.dialog.configure(bg=self.colors["bg"])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 200) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

        # Attendre que le dialog soit fermé (rendre vraiment modal)
        parent.wait_window(self.dialog)

    def _create_widgets(self):
        """Crée les widgets."""
        main_frame = tk.Frame(self.dialog, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # ID
        tk.Label(
            main_frame,
            text="ID (slug, ex: summarize) :",
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        ).pack(anchor='w')

        self.id_entry = tk.Entry(
            main_frame,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["text_cursor"],
            font=('Segoe UI', 10)
        )
        self.id_entry.pack(fill='x', pady=(0, 10))

        # Label
        tk.Label(
            main_frame,
            text="Label (ex: Résumer) :",
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

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        btn_frame.pack(fill='x', pady=(10, 0))

        tk.Button(
            btn_frame,
            text="Créer",
            command=self._create,
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

    def _create(self):
        """Crée le prompt."""
        action_id = self.id_entry.get().strip().lower().replace(' ', '_')
        label = self.label_entry.get().strip()

        if not action_id or not label:
            messagebox.showerror("Erreur", "L'ID et le label sont obligatoires")
            return

        # Créer avec un prompt template par défaut
        default_prompt = f"[Votre instruction ici]\n\nTexte : {{text}}"
        prompt_manager.save_custom_prompt(action_id, label, default_prompt)

        self.result = True
        self.dialog.destroy()
