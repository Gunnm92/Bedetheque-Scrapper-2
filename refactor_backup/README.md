# Structure du dossier `src/`

La refonte du plugin BDbase Scraper repose maintenant sur des modules **plats** situés à la racine de `src/`. L’objectif est d’éviter les sous-packages pour rester compatible avec l’installateur ComicRack.

## Organisation des fichiers

```
src/
├── BDbaseScraper.py         # Entrée ComicRack (hooks, configuration rapide)
├── config.py                # Constantes, flags, patterns, cookies
├── utils.py                 # Helpers HTTP, parsing, logging, formatage
├── settings.py              # Chargement/sauvegarde App.Config + traductions
├── scraper.py               # Parsing des séries/albums/revues + BD_start/QuickScrape
├── ui_forms.py              # Dialogues (ProgressBar, BDConfigForm, SeriesForm, DirectScrape)
├── BDTranslations.Config    # Trads FR/EN
├── Package.ini             # Métadonnées du plugin ComicRack
├── assets/                 # Icônes et ressources graphiques
└── stdlib/                 # Modules Python 2.7 nécessaires (IronPython)
```

## Modules refactorés

### `config.py`
- Déclare les URLs de BDbase, les expressions régulières, les flags `CB*`, `SHOW*`, `TIMEOUT`, etc.
- Contient les variables globales partagées (flags runtime, cookies).

### `utils.py`
- Enveloppe les appels HTTP (`_read_url`, `GetFullURL`), la manipulation de texte (`normalize_text`, `strip_tags`), et le logging (`debuglog`, `log_BD`).
- Inclut des utilitaires pour analyser les numéros d’album, gérer les noms d’auteurs et vérifier les dates.

### `settings.py`
- Gère la persistance XML via `AppSettings`.
- Expose `LoadSetting()`, `SaveSetting()` et `Translate()`/`Trans()` pour récupérer la localisation.
- Fournit `get_plugin_path()` (retourne la racine `src/`).

### `scraper.py`
- Contient `parseSerieInfo`, `parseAlbumInfo`, `parseRevueInfo`, `AlbumChooser`, `SetAlbumInformation`.
- Implémente `BD_start()`/`QuickScrapeBDbase()` qui orchestrent les dialogues (`ProgressBarDialog`, `SeriesForm`, `DirectScrape`).
- Ajoute les helpers `download_cover`, `search_series`, `find_best_match`, `normalize_album_number`, `is_oneshot`, `extract_authors_from_html`.

### `ui_forms.py`
- Crée `ProgressBarDialog`, `BDConfigForm`, `SeriesForm`, `DirectScrape`, `HighDpiHelper`.
- Lie les options à `settings.LoadSetting()`/`SaveSetting()` et déclenche `config.AllowUserChoice`, `TIMEPOPUP`, etc.
- Gère l’apparition des dialogues (cancel, timer, choix multiples) de manière identique à l’original.

## Ressources et dépendances

- **`assets/`** : icônes `BDbase.png`, `BDbaseQ.png`, `BDbase.ico` et fichiers SVG.
- **`stdlib/`** : collection (29 fichiers) des modules Python 2.7 nécessaires pour IronPython.
- **`BDTranslations.Config`** : contient les labels en FR/EN référencés par `Trans(index)`.

## Notes

1. Les fichiers sont désormais importables directement, par exemple :
   ```python
   import scraper
   import ui_forms
   import settings
   ```
2. `BDbaseScraper.py` restera le point d’entrée ComicRack, mais délègue l’essentiel du travail aux nouveaux modules.
3. Continue à utiliser `python3 -m py_compile src/*.py` pour valider la syntaxe sous IronPython.

---

**Date de mise à jour**: 2026-02-06
