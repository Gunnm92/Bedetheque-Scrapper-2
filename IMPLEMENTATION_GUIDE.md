# 🔧 Guide d'Implémentation - Phase 3

**Date**: 2026-02-05
**Phase**: 3 - Implémentation
**Objectif**: Finaliser l'implémentation des modules `scraper.py` et `ui_forms.py`

---

## 📋 État Actuel

### ✅ Complètement Implémenté
- **config.py** (200 lignes) - 100%
- **utils.py** (400 lignes) - 100%
- **settings.py** (220 lignes) - 100%

### 🏗️ Structure Créée (TODO markers)
- **scraper.py** (380 lignes) - Structure complète, logique à implémenter
- **ui_forms.py** (650 lignes) - Composants UI créés, certains détails à compléter

**Total**: ~1850 lignes structurées

---

## 🎯 Stratégie d'Implémentation

### Approche Recommandée: **Progressive et Testable**

Au lieu de tout copier d'un coup, implémenter fonction par fonction en testant au fur et à mesure.

---

## 📦 scraper.py - Plan d'Implémentation

### Priorité 1: Fonctions Core (Critiques)

#### 1. `parseAlbumInfo_bdbase()` ⚠️ CRITIQUE
**Localisation originale**: Lignes 1099-1568 (~470 lignes)
**Complexité**: Haute - Parse toutes les métadonnées

**À implémenter**:
- Extraction série (BDBASE_ALBUM_SERIE)
- Extraction titre (ALBUM_TITLE_PATTERN)
- Gestion numéros (Number, AlternateNumber, HS)
- Extraction éditeur/collection
- Extraction résumé
- Parsing détails (date, ISBN, pages, etc.)
- Extraction auteurs (writer, penciller, colorist, etc.)
- Téléchargement couverture
- Gestion LD+JSON fallback

**Méthode**:
```python
# Copier du fichier original (lignes 1099-1568)
# Adapter les imports pour utiliser nos modules:
# - config.CB* au lieu de variables globales
# - utils.parseName(), strip_tags(), etc.
# - settings.Trans() pour traductions
```

#### 2. `parseSerieInfo()` ⚠️ CRITIQUE
**Localisation originale**: Lignes 667-1072 (~405 lignes)
**Complexité**: Haute - Gère séries et revues

**À implémenter**:
- Téléchargement page série
- Extraction métadonnées série (genre, statut, résumé, note)
- Gestion revues (/revue-* URLs)
- Liste d'albums
- Choix utilisateur (AlbumChooser)
- Mise à jour book avec info série

**Méthode**:
```python
# Copier lignes 667-1072
# Adapter imports et variables globales
```

#### 3. `parseAlbumInfo()` 🔶 IMPORTANT
**Localisation originale**: Lignes 1075-1098 (~24 lignes)
**Complexité**: Basse - Wrapper

**À implémenter**:
```python
def parseAlbumInfo(book, pageUrl, num, lDirect=False):
    # Télécharge HTML
    albumHTML = _read_url(pageUrl, False)
    # Appelle parseAlbumInfo_bdbase
    return parseAlbumInfo_bdbase(book, pageUrl, num, albumHTML)
```

### Priorité 2: Fonctions de Support

#### 4. `BD_start()` 🔶 IMPORTANT
**Localisation originale**: Lignes 207-640 (~433 lignes)
**Complexité**: Haute - Point d'entrée principal

**À implémenter** (après parseSerieInfo/parseAlbumInfo):
- Chargement settings
- Boucle sur books
- Extraction info livre (series, number)
- Recherche série
- Appel parseSerieInfo/parseAlbumInfo
- Gestion erreurs
- Statistiques finales

#### 5. `AlbumChooser()` 🔷 MOYEN
**Localisation originale**: Dispersée
**Complexité**: Moyenne - UI selection

**À implémenter**:
```python
def AlbumChooser(ListAlbum):
    from ui_forms import SeriesForm, FormType
    form = SeriesForm("Albums", ListAlbum, FormType.ALBUM)
    result = form.ShowDialog()
    if result == DialogResult.OK:
        return NewLink  # Variable globale mise à jour par form
    return None
```

#### 6. `parseRevueInfo()` 🔷 MOYEN
**Localisation originale**: Lignes ~1570-1660 (~90 lignes)
**Pour magazines/revues uniquement**

#### 7. Fonctions Helper 🔵 FACILE
- `download_cover()` - Lignes ~600-640
- `search_series()` - À extraire
- `SetAlbumInformation()` - Lignes 644-666
- `SetSerieId()` - À extraire

---

## 📦 ui_forms.py - Plan d'Implémentation

### État Actuel
- ✅ Squelette complet de toutes les classes
- ✅ Composants UI principaux créés
- 🔷 Certains détails à compléter (event handlers, layouts)

### À Compléter

#### 1. `BDConfigForm` 🔶 IMPORTANT
**Localisation originale**: Lignes 2026-2856 (~830 lignes)

**TODO**:
- Compléter les 3 onglets (tabPage1, tabPage2, tabPage3)
- Ajouter tous les contrôles (~50 checkboxes, textboxes, radio buttons)
- Implémenter `button_Click()` complètement (sauvegarder tous settings)

**Méthode**: Copier la logique complète depuis l'original

#### 2. `ProgressBarDialog` 🔷 MOYEN
**Localisation originale**: Lignes ~1580-1670

**TODO**:
- Ajouter ProgressBar component
- Implémenter Update() avec mise à jour visuelle
- Ajouter Cancel button
- Afficher cover thumbnail

#### 3. `SeriesForm` ✅ QUASI-COMPLET
Déjà bien implémenté, juste tester

#### 4. `DirectScrape` ✅ QUASI-COMPLET
Déjà bien implémenté, juste tester

---

## 🔄 Ordre d'Implémentation Recommandé

### Étape 1: Core Parsing (Critique) ⚠️
1. **parseAlbumInfo_bdbase()** - Le cœur du parsing
2. **parseSerieInfo()** - Extraction info série
3. **parseAlbumInfo()** - Wrapper simple

**Temps estimé**: 2-3 heures
**Fichiers touchés**: `scraper.py`

### Étape 2: Entry Point 🔶
4. **BD_start()** - Point d'entrée principal
5. **AlbumChooser()** - Sélection albums

**Temps estimé**: 1-2 heures
**Fichiers touchés**: `scraper.py`

### Étape 3: UI Finalization 🔷
6. **BDConfigForm** - Compléter le dialogue config
7. **ProgressBarDialog** - Compléter la progress bar

**Temps estimé**: 2-3 heures
**Fichiers touchés**: `ui_forms.py`

### Étape 4: Integration & Tests 🧪
8. Créer nouveau `BDbaseScraper.py` minimaliste
9. Ajuster les chemins de fichiers
10. Tests avec ComicRack

**Temps estimé**: 2-3 heures

---

## 💻 Méthode de Travail

### Pour Chaque Fonction

1. **Localiser** dans le fichier original (numéros de lignes donnés ci-dessus)
2. **Copier** le code
3. **Adapter** les imports:
   ```python
   # Avant (original)
   if CBISBN:
       book.ISBN = isbn

   # Après (module)
   import config
   if config.CBISBN:
       book.ISBN = isbn
   ```
4. **Remplacer** les appels de fonctions:
   ```python
   # Avant
   titre = titlize(raw_title)

   # Après
   from utils import titlize
   titre = titlize(raw_title)
   ```
5. **Tester** individuellement si possible

### Variables Globales à Gérer

Les variables globales du fichier original sont maintenant:
- Dans **config.py**: CB*, SHOW*, VERSION, etc.
- Dans **scraper.py**: dlgName, dlgNumber, bStopit, etc.

**Migration**:
```python
# Original: variable globale directe
global CBISBN
if CBISBN:
    ...

# Nouveau: import depuis config
import config
if config.CBISBN:
    ...
```

---

## 📝 Checklist d'Implémentation

### scraper.py
- [ ] parseAlbumInfo_bdbase() - Parsing album complet
- [ ] parseSerieInfo() - Parsing série complet
- [ ] parseAlbumInfo() - Wrapper
- [ ] BD_start() - Entry point
- [ ] AlbumChooser() - Sélection
- [ ] parseRevueInfo() - Magazines
- [ ] download_cover() - Couvertures
- [ ] SetAlbumInformation() - Finalisation
- [ ] search_series() - Recherche
- [ ] Autres helpers

### ui_forms.py
- [ ] BDConfigForm - Tous les onglets et contrôles
- [ ] BDConfigForm.button_Click() - Sauvegarde complète
- [ ] ProgressBarDialog - ProgressBar + Update()
- [ ] Tester SeriesForm
- [ ] Tester DirectScrape

### Intégration
- [ ] Nouveau BDbaseScraper.py (point d'entrée)
- [ ] Ajuster chemins fichiers (get_plugin_path())
- [ ] Corriger imports circulaires si besoin
- [ ] Tests unitaires si possible
- [ ] Test avec ComicRack

---

## 🎯 Objectif de la Phase 3

**Résultat attendu**: Plugin ComicRack fonctionnel avec la nouvelle architecture

**Critères de succès**:
- ✅ scraper.py implémenté et fonctionnel
- ✅ ui_forms.py implémenté et fonctionnel
- ✅ Nouveau BDbaseScraper.py créé
- ✅ Plugin teste avec ComicRack sans erreurs
- ✅ Toutes les fonctionnalités originales préservées

---

## 🚀 Démarrage Rapide

Pour commencer **maintenant**, voici la première tâche concrète:

### TÂCHE 1: Implémenter parseAlbumInfo_bdbase()

```bash
# 1. Ouvrir le fichier original
nano src/BDbaseScraper.py +1099

# 2. Copier les lignes 1099-1568 (fonction parseAlbumInfo_bdbase)

# 3. Ouvrir le module
nano src/bdbase_scraper/scraper.py

# 4. Remplacer la fonction placeholder par l'implémentation

# 5. Adapter les imports et variables globales

# 6. Tester l'import:
python -c "from bdbase_scraper import scraper; print('OK')"
```

---

**Prêt à commencer** ? Suivez ce guide étape par étape pour une implémentation propre et testable.

**Prochaine étape**: Implémenter `parseAlbumInfo_bdbase()` (fonction la plus critique)
