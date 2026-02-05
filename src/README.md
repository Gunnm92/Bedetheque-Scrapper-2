# Structure du dossier src/

Cette structure organise le code du plugin BDbase Scraper de manière modulaire et maintenable.

## Structure des dossiers

```
src/
├── bdbase_scraper/          # Code principal du plugin (modules refactorés)
│   ├── __init__.py          # Initialisation du package
│   ├── config.py            # Constantes, regex patterns, feature flags
│   └── utils.py             # Fonctions utilitaires (parsing, HTTP, logging)
│
├── stdlib/                  # Bibliothèque standard Python (IronPython 2.7)
│   ├── collections.py       # Types de collections Python
│   ├── urllib.py            # Gestion des URLs
│   ├── HTMLParser.py        # Parser HTML
│   └── ...                  # Autres modules stdlib nécessaires
│
├── assets/                  # Ressources graphiques
│   ├── BDbase.png           # Icône principale
│   ├── BDbaseQ.png          # Icône QuickScrape
│   ├── BDbase.ico           # Icône Windows
│   └── *.svg                # Sources vectorielles
│
├── BDbaseScraper.py         # Point d'entrée principal (fichier monolithique original)
├── BDTranslations.Config    # Traductions FR/EN
└── Package.ini              # Configuration du package ComicRack
```

## Modules refactorés (bdbase_scraper/)

### config.py
Contient toutes les configurations et constantes :
- Version, URLs de base (BASE_URL, BASE_DOMAIN)
- Patterns regex pour le scraping (SERIE_*, ALBUM_*, REVUE_*)
- Feature flags (CB*, SHOW*, DBG*)
- Variables de configuration runtime

### utils.py
Fonctions utilitaires réutilisables :
- **HTTP** : `_read_url()`, `url_fix()`, `GetFullURL()`
- **Parsing** : `parse_date_fr()`, `extract_number_from_title()`, `extract_ld_json()`
- **Texte** : `normalize_text()`, `remove_accents()`, `strip_tags()`, `checkWebChar()`
- **Formatage** : `titlize()`, `cleanARTICLES()`, `formatARTICLES()`
- **Logging** : `debuglog()`, `debuglogOnError()`, `log_BD()`
- **Validation** : `isnumeric()`, `isPositiveInt()`

## À venir (refactoring en cours)

### settings.py
- Classe `AppSettings` pour la gestion XML
- `LoadSetting()` / `SaveSetting()`
- Système de traductions

### scraper.py
- Logique de scraping principale
- `parseSerieInfo()`, `parseAlbumInfo()`, `parseRevueInfo()`
- `BD_start()`, `WorkerThread()`

### ui_forms.py
- Formulaires d'interface utilisateur
- `ProgressBarDialog`, `BDConfigForm`, `SeriesForm`, `DirectScrape`
- `HighDpiHelper` pour le support des écrans haute résolution

## Bibliothèque standard (stdlib/)

Le dossier `stdlib/` contient les modules Python 2.7 nécessaires car ComicRack utilise IronPython.
Ces fichiers proviennent de la bibliothèque standard Python et sont inclus pour garantir la compatibilité.

## Ressources (assets/)

Les fichiers graphiques utilisés par le plugin :
- **BDbase.png** : Icône principale du scraper
- **BDbaseQ.png** : Icône pour le QuickScrape
- **BDbase.ico** : Icône Windows pour les dialogues
- **SVG** : Sources vectorielles pour régénérer les icônes si nécessaire

## Notes importantes

1. **Compatibilité** : Le code doit rester compatible avec :
   - ComicRack (application hôte)
   - IronPython 2.7
   - .NET Framework

2. **Chemins de fichiers** : Le plugin utilise `__file__` pour trouver ses ressources.
   Avec la nouvelle structure, les chemins doivent être ajustés.

3. **Imports** : Les nouveaux modules dans `bdbase_scraper/` peuvent être importés :
   ```python
   from bdbase_scraper import config, utils
   ```

4. **Fichier original** : `BDbaseScraper.py` reste intact pendant le refactoring
   pour garantir que le plugin continue de fonctionner.

## Progression du refactoring

- ✅ config.py - Fait
- ✅ utils.py - Fait
- ⏳ settings.py - À faire
- ⏳ scraper.py - À faire
- ⏳ ui_forms.py - À faire
- ⏳ BDbaseScraper.py (refactoré) - À faire

---

**Date de création** : 2026-02-05
**Branche** : refactoring/split-main-file
