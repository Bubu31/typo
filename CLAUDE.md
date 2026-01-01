# Typo - Correcteur orthographique système

## Description
Application Windows en Python qui tourne dans le system tray et permet de corriger/formater du texte via l'API Claude. Inclut aussi un système de snippets (textes prédéfinis).

## Build
```bash
python -m PyInstaller Typo.spec --noconfirm
cp dist/Typo.exe "E:\CustomScript\Typo.exe"
```

## Architecture
- `main.py` - Point d'entrée, gestion des hotkeys avec pynput
- `tray.py` - Icône system tray avec pystray
- `api_client.py` - Appels à l'API Claude
- `clipboard.py` - Gestion du presse-papier
- `snippet_manager.py` - Gestion des snippets (CRUD)
- `ui_snippets.py` - Interface Tkinter pour les snippets
- `ui_hotkeys.py` - Interface pour personnaliser les raccourcis
- `ui_prompts.py` - Interface pour personnaliser les prompts
- `settings_manager.py` - Gestion de la config JSON
- `hotkey_manager.py` - Validation et parsing des raccourcis

## Raccourcis clavier
- **Ctrl+Alt+C** : Corriger le texte sélectionné
- **Ctrl+Alt+F** : Formater
- **Ctrl+Alt+R** : Reformuler
- **Ctrl+Alt+P** : Rédiger US/Bug/Message
- **Ctrl+Alt+T** : Traduire en anglais
- **Ctrl+Alt+,** : Afficher l'aide
- **Ctrl+Shift+1-9** : Coller un snippet (slot 1-9)

## Fichiers de config
Emplacement : `C:\Users\mathi\AppData\Roaming\Typo\`
- `config.json` - Configuration générale (clé API, hotkeys, langue)
- `snippets.json` - Liste des snippets
- `prompts.json` - Prompts personnalisés

## Points d'attention
- **Tkinter + pystray** : Les callbacks pystray s'exécutent dans un thread séparé. Ne pas utiliser `wait_window()` dans les dialogs modaux, utiliser un pattern callback à la place.
- **Clavier français** : Ctrl+Alt = AltGr, donc les snippets utilisent Ctrl+Shift au lieu de Ctrl+Alt pour éviter les conflits.
- **VK codes numpad** : Rangée supérieure 49-57, numpad 97-105

## Dépendances principales
- anthropic
- pynput
- pystray
- pyperclip
- Pillow
