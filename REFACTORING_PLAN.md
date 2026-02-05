# Plan de Refactoring - BDbase Scraper

## État actuel
- **Fichier principal**: `src/BDbaseScraper.py` - **3524 lignes**
- Tout le code est dans un seul fichier monolithique
- Difficile à maintenir et à tester

## Objectif
Séparer le code en modules logiques tout en préservant la compatibilité avec ComicRack

## Architecture proposée

### 1. `config.py` ✅ FAIT
**Contenu**:
- Toutes les constantes globales (VERSION, BASE_URL, etc.)
- Toutes les regex patterns (SERIE_*, ALBUM_*, REVUE_*)
- Feature flags (CB*, SHOW*, etc.)
- Configuration par défaut

**Lignes**: ~200 lignes

### 2. `utils.py` ✅ FAIT
**Contenu**:
- Fonctions de parsing (parse_date_fr, extract_number_from_title, etc.)
- Fonctions de nettoyage de texte (normalize_text, remove_accents, strip_tags, etc.)
- Fonctions de formatage (titlize, cleanARTICLES, formatARTICLES, etc.)
- Fonctions HTTP (_read_url, url_fix, GetFullURL, etc.)
- Fonctions de logging (debuglog, debuglogOnError, log_BD, etc.)
- Utilitaires divers (isnumeric, if_else, sstr, etc.)

**Lignes**: ~400 lignes

### 3. `scraper.py` 📝 À FAIRE
**Contenu**:
- `BD_start(books)` - Point d'entrée principal du scraping
- `WorkerThread(books)` - Thread de travail
- `SetSerieId(book, serie, num, nBooksIn)` - Configuration série/ID
- `SetAlbumInformation(book, serieUrl, serie, num)` - Info album
- `parseSerieInfo(book, serieUrl, lDirect)` - Parse info série
- `parseAlbumInfo(book, pageUrl, num, lDirect)` - Parse info album
- `parseAlbumInfo_bdbase(book, pageUrl, num, albumHTML)` - Parse spécifique BDbase
- `parseRevueInfo(book, SerieInfoRegex, serieUrl, Numero, serie)` - Parse revue
- `AlbumChooser(ListAlbum)` - Sélection d'album
- `QuickScrapeBDbase(books, book, cLink)` - Quick scrape

**Lignes estimées**: ~1500 lignes

### 4. `settings.py` 📝 À FAIRE
**Contenu**:
- Classe `AppSettings` - Gestion XML des paramètres
- `LoadSetting()` - Charger configuration
- `SaveSetting()` - Sauvegarder configuration
- `Translate()` - Chargement traductions
- `Trans(nWord)` - Fonction de traduction
- Helper functions: `ft()`, `tf()`

**Lignes estimées**: ~300 lignes

### 5. `ui_forms.py` 📝 À FAIRE
**Contenu**:
- Classe `ProgressBarDialog(Form)` - Dialogue barre de progression
- Classe `BDConfigForm(Form)` - Dialogue de configuration
- Classe `SeriesForm(Form)` - Dialogue sélection série/album
- Classe `DirectScrape(Form)` - Dialogue scrape direct (quick scrape)
- Classe `HighDpiHelper` - Gestion DPI élevé
- Fonction `ThemeMe(control)` - Application thème ComicRack
- Enum `FormType` (SERIE, ALBUM, EDITION)

**Lignes estimées**: ~1100 lignes

### 6. `BDbaseScraper.py` (refactoré) 📝 À FAIRE
**Contenu**:
- En-tête ComicRack (@Name, @Key, @Hook, @Image, @Description)
- Imports de tous les modules
- Hooks ComicRack:
  - `ConfigureBDbaseQuick()` - @Hook ConfigScript
  - `ConfigureBDbase(self)` - @Hook Library
  - `QuickScrapeBDbase(books)` - @Hook Books

**Lignes estimées**: ~50-100 lignes

## Structure des dépendances

```
BDbaseScraper.py (entry point)
├── config.py (constants, patterns)
├── utils.py (helpers)
│   └── imports: config
├── settings.py (config management)
│   └── imports: config, utils
├── scraper.py (scraping logic)
│   └── imports: config, utils, ui_forms, settings
└── ui_forms.py (UI dialogs)
    └── imports: config, utils, settings
```

## Stratégie de migration

### Phase 1: Modules de base ✅
1. ✅ Créer `config.py` avec toutes les constantes
2. ✅ Créer `utils.py` avec les fonctions utilitaires
3. ✅ Créer la branche `refactoring/split-main-file`

### Phase 2: Logique métier (EN COURS)
4. Créer `settings.py` avec la gestion de configuration
5. Créer `scraper.py` avec la logique de scraping
6. Tester les imports et dépendances

### Phase 3: Interface utilisateur
7. Créer `ui_forms.py` avec tous les formulaires
8. Vérifier les dépendances circulaires

### Phase 4: Intégration
9. Refactorer `BDbaseScraper.py` comme point d'entrée minimal
10. Tester avec ComicRack
11. Valider que toutes les fonctionnalités marchent

### Phase 5: Tests et finalisation
12. Tests complets de toutes les fonctionnalités
13. Commit et merge vers main
14. Mettre à jour la documentation

## Points d'attention

### Variables globales
Beaucoup de variables globales sont utilisées partout:
- `dlgName`, `dlgNumber`, `dlgAltNumber` - Info livre en cours
- `bStopit` - Flag d'arrêt
- `NewLink`, `NewSeries` - Résultats sélection UI
- `TimerExpired`, `SkipAlbum` - Flags UI
- `Serie_Resume` - Résumé série
- `AlbumNumNum`, `Shadow1`, `Shadow2` - Flags parsing
- `aWord` - Dictionnaire traductions

**Solution**: Ces variables devront être passées comme paramètres ou encapsulées dans des classes/contextes.

### Dépendances ComicRack
Le code dépend fortement de ComicRack:
- `from cYo.Projects.ComicRack.Engine import *`
- Accès à `ComicRack.App`, `ComicRack.MainWindow`, etc.

**Solution**: Garder ces imports dans les modules qui en ont besoin.

### Compatibilité
Le plugin doit rester compatible avec:
- ComicRack (application hôte)
- IronPython 2.7
- .NET Framework

## Avantages du refactoring

1. **Maintenabilité**: Code organisé en modules logiques
2. **Testabilité**: Possibilité de tester chaque module séparément
3. **Lisibilité**: Fichiers plus courts et focalisés
4. **Réutilisabilité**: Fonctions utilitaires réutilisables
5. **Évolutivité**: Plus facile d'ajouter de nouvelles fonctionnalités

## Prochaines étapes

1. Créer `settings.py` pour la gestion de configuration
2. Extraire la logique de scraping dans `scraper.py`
3. Extraire les formulaires dans `ui_forms.py`
4. Refactorer le point d'entrée `BDbaseScraper.py`
5. Tests exhaustifs

---

**Date de création**: 2026-02-05
**Branche**: `refactoring/split-main-file`
**Status**: EN COURS (Phase 2)
