# Typo - Correcteur orthographique intelligent

> Correcteur orthographique système avec IA pour Windows, propulsé par Claude AI

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://github.com/Bubu31/typo/releases)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Typo** est un correcteur orthographique système qui s'intègre directement dans votre workflow Windows. Sélectionnez du texte, appuyez sur un raccourci, et obtenez instantanément une correction, reformulation ou traduction grâce à l'IA Claude.

---

## ✨ Fonctionnalités principales

### 🔤 Correction intelligente
- **Correction simple** : Corrige les fautes d'orthographe et de grammaire
- **Formatage** : Améliore la ponctuation et la mise en forme
- **Reformulation** : Rend le texte plus clair et fluide
- **Rédaction professionnelle** : Transforme vos notes en User Stories, bugs ou messages clients structurés
- **Traduction** : Traduit instantanément en anglais

### 🌍 Multi-langues (v1.3.0)
- Support de **4 langues** : Français 🇫🇷, English 🇬🇧, Español 🇪🇸, Deutsch 🇩🇪
- Sélection rapide dans le menu tray
- Tous les prompts traduits

### 📝 Snippets (v1.3.0)
- Bibliothèque de textes réutilisables
- Insertion rapide via **Ctrl+Alt+1-9**
- Recherche intelligente avec **Ctrl+Alt+S**
- Gestion complète : créer, éditer, supprimer

### 🎨 Prompts personnalisés (v1.3.0)
- Créez vos propres actions (Résumer, Simplifier, etc.)
- Overridez les prompts par défaut
- Interface de gestion intuitive

### ⌨️ Raccourcis personnalisables (v1.3.0)
- Modifiez tous les raccourcis selon vos préférences
- Détection automatique des conflits
- Interface de configuration avec capture clavier

### 🌓 Mode sombre (v1.3.0)
- Détection automatique du thème Windows
- S'adapte en temps réel
- Appliqué à toutes les fenêtres

### 🚀 Autres fonctionnalités
- **Icône system tray** : Contrôle discret depuis la barre des tâches
- **Démarrage automatique** : Lance Typo au démarrage de Windows
- **Mises à jour automatiques** : Détection et installation des nouvelles versions
- **Workflow non-intrusif** : S'intègre à n'importe quelle application

---

## 📥 Installation

### Prérequis
- Windows 10/11
- Une clé API Anthropic ([obtenir ici](https://console.anthropic.com))

### Méthode 1 : Télécharger l'exécutable (recommandé)

1. Téléchargez la dernière version depuis les [Releases](https://github.com/Bubu31/typo/releases)
2. Exécutez `Typo.exe`
3. Entrez votre clé API Anthropic au premier lancement
4. C'est prêt ! 🎉

### Méthode 2 : Installation depuis les sources

```bash
# Cloner le repository
git clone https://github.com/Bubu31/typo.git
cd typo

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

---

## 🎯 Utilisation

### Workflow de base

1. **Sélectionnez du texte** dans n'importe quelle application
2. **Appuyez sur un raccourci** :
   - `Ctrl+Alt+C` : Corriger
   - `Ctrl+Alt+F` : Formater
   - `Ctrl+Alt+R` : Reformuler
   - `Ctrl+Alt+P` : Rédiger (US/Bug/Message)
   - `Ctrl+Alt+T` : Traduire en anglais
3. Le texte est **automatiquement remplacé** par la version corrigée

### Utilisation des snippets

**Insertion rapide** :
- `Ctrl+Alt+1` à `Ctrl+Alt+9` : Insérer le snippet assigné au slot

**Recherche** :
- `Ctrl+Alt+S` : Ouvrir la fenêtre de recherche
- Tapez pour filtrer, `Entrée` pour insérer

**Gestion** :
- Menu tray → Snippets → Gérer les snippets...
- Créer, éditer, supprimer, assigner des raccourcis

### Menu system tray

Clic droit sur l'icône Typo dans la barre des tâches :

```
🟢 Activer/Désactiver
────────────────────
⌨️  Raccourcis
📋 Snippets
────────────────────
🌍 Langue / Language
────────────────────
⚙️  Paramètres
   ├─ Personnaliser les raccourcis...
   ├─ Gérer les prompts...
   └─ ✓ Démarrer avec Windows
────────────────────
ℹ️  Version 1.3.0
🔄 Vérifier les mises à jour
────────────────────
❌ Quitter
```

---

## ⚙️ Configuration

### Fichiers de configuration

Typo stocke ses paramètres dans `%APPDATA%\Typo\` :

- **`config.json`** : Paramètres principaux (langue, clé API, raccourcis)
- **`prompts.json`** : Prompts personnalisés
- **`snippets.json`** : Bibliothèque de snippets

### Migration automatique

Au premier lancement de la v1.3.0, Typo migre automatiquement votre configuration depuis l'ancien fichier `.env` vers le nouveau système.

### Personnalisation des prompts

**Créer un prompt custom** :
1. Menu tray → Paramètres → Gérer les prompts...
2. Cliquer sur "+ Nouveau prompt custom"
3. Définir l'ID (ex: `summarize`) et le label (ex: "Résumer")
4. Écrire le prompt (doit contenir `{text}`)
5. Enregistrer

**Override un prompt par défaut** :
1. Sélectionner un prompt par défaut dans la liste
2. Modifier le texte du prompt
3. Enregistrer

**Exemple de prompt custom** :
```
Résume ce texte en 3 phrases maximum, en gardant les points clés.

Texte : {text}
```

### Personnalisation des raccourcis

1. Menu tray → Paramètres → Personnaliser les raccourcis...
2. Sélectionner une action et cliquer sur "Modifier"
3. Appuyer sur la nouvelle combinaison de touches
4. Valider (détection automatique des conflits)
5. Enregistrer et redémarrer l'application

---

## ⌨️ Raccourcis clavier par défaut

| Raccourci | Action | Description |
|-----------|--------|-------------|
| `Ctrl+Alt+C` | Corriger | Corrige l'orthographe et la grammaire |
| `Ctrl+Alt+F` | Formater | Corrige + améliore la ponctuation |
| `Ctrl+Alt+R` | Reformuler | Rend le texte plus clair |
| `Ctrl+Alt+P` | Rédiger | Transforme en US/Bug/Message |
| `Ctrl+Alt+T` | Traduire | Traduit en anglais |
| `Ctrl+Alt+,` | Aide | Affiche les raccourcis |
| `Ctrl+Alt+1-9` | Snippet | Insère le snippet assigné |
| `Ctrl+Alt+S` | Rechercher | Ouvre la recherche de snippets |

> 💡 **Tous les raccourcis sont personnalisables !**

---

## 🎨 Thèmes

Typo détecte automatiquement le thème de votre système Windows et adapte son interface :

- **Mode clair** : Fond blanc, texte noir
- **Mode sombre** : Fond gris foncé, texte blanc

L'icône de la barre des tâches s'adapte également pour une meilleure visibilité.

---

## 🔧 Développement

### Structure du projet

```
typo/
├── main.py                  # Point d'entrée
├── api_client.py           # Client API Claude
├── clipboard.py            # Gestion du clipboard
├── config.py               # Configuration legacy
├── ui.py                   # Fenêtres UI principales
├── tray.py                 # Icône system tray
├── startup.py              # Démarrage Windows
├── updater.py              # Système de mise à jour
│
├── settings_manager.py     # Gestion configuration centralisée
├── theme_manager.py        # Détection thème Windows
├── hotkey_manager.py       # Validation raccourcis
├── prompt_manager.py       # Gestion prompts custom
├── snippet_manager.py      # Gestion snippets
├── translations.py         # Prompts multi-langues
│
├── ui_prompts.py           # Fenêtre gestion prompts
├── ui_snippets.py          # Fenêtre gestion snippets
├── ui_hotkeys.py           # Fenêtre gestion raccourcis
│
├── version.py              # Numéro de version
└── requirements.txt        # Dépendances Python
```

### Dépendances

```txt
pynput>=1.7.6          # Capture des raccourcis clavier
pyperclip>=1.8.2       # Gestion du clipboard
anthropic>=0.18.0      # API Claude
pystray>=0.19.4        # Icône system tray
Pillow>=10.0.0         # Génération d'images (icône)
python-dotenv>=1.0.0   # Gestion .env
```

### Builder l'exécutable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Typo main.py
```

L'exécutable sera dans `dist/Typo.exe`.

### Architecture des managers

**Principe de séparation des responsabilités** :

- **settings_manager** : Unique source de vérité pour la configuration
- **prompt_manager** : Abstraction pour les prompts (default + custom + overrides)
- **snippet_manager** : CRUD snippets avec recherche
- **hotkey_manager** : Validation, conversion VK codes, détection conflits
- **theme_manager** : Lecture Registry Windows pour le thème
- **translations** : Prompts traduits en 4 langues

---

## 📋 Notes de version

### v1.3.0 (Décembre 2024)

**🎉 Mise à jour majeure avec 5 nouvelles fonctionnalités**

✨ **Nouvelles fonctionnalités** :
- Support multi-langues (FR/EN/ES/DE)
- Prompts personnalisés (créer vos propres actions)
- Bibliothèque de snippets avec recherche
- Raccourcis clavier personnalisables
- Mode sombre avec détection automatique

🏗️ **Architecture** :
- 9 nouveaux modules (managers + UI)
- Configuration centralisée dans `%APPDATA%\Typo\`
- Migration automatique depuis `.env`

🎨 **UI** :
- Menu tray complètement refait
- 3 nouvelles fenêtres de configuration
- Théming appliqué partout

### v1.2.0 (Décembre 2024)
- Système de mise à jour automatique
- Détection de nouvelles versions
- Téléchargement et installation auto

### v1.1.0 (Décembre 2024)
- Démarrage automatique avec Windows
- Workflow GitHub Actions pour releases

### v1.0.0 (Décembre 2024)
- Version initiale
- 5 actions de base (corriger, formater, reformuler, professionnel, traduire)
- Icône system tray

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Anthropic](https://www.anthropic.com/) pour l'API Claude
- [pynput](https://github.com/moses-palmer/pynput) pour la capture des raccourcis
- [pystray](https://github.com/moses-palmer/pystray) pour l'icône system tray

---

## 📧 Contact & Support

- **Issues** : [GitHub Issues](https://github.com/Bubu31/typo/issues)
- **Releases** : [GitHub Releases](https://github.com/Bubu31/typo/releases)

---

<p align="center">
  Fait avec ❤️ et <a href="https://www.anthropic.com/claude">Claude AI</a>
</p>

<p align="center">
  <sub>🤖 Generated with <a href="https://claude.com/claude-code">Claude Code</a></sub>
</p>
