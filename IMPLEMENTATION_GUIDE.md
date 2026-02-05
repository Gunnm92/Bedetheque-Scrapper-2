# 🔧 Guide d'Implémentation - Phase 3

**Date**: 2026-02-05
**Phase**: 3 - Implémentation (en cours)
**Objectif**: Finaliser le moteur de scraping restructuré (`scraper.py` + `ui_forms.py`) et basculer les hooks dans le point d'entrée refactoré.

---

## 📋 État actuel

### ✅ Modules opérationnels
- `config.py` (200 lignes) : constantes, flags, patterns
- `utils.py` (400 lignes) : helpers HTTP, texte, logging, parse
- `settings.py` (220 lignes) : gestion XML + traduction (version allégée mais fonctionnelle)

### 🔄 Modules en cours
- `scraper.py` : `parseSerieInfo`, `parseAlbumInfo`, `parseAlbumInfo_bdbase`, `AlbumChooser`, `parseRevueInfo` et `SetAlbumInformation` sont portés ; `BD_start()`/`QuickScrapeBDbase()` et les helpers `search_series`, `find_best_match`, `normalize_album_number` restent à intégrer.
- `ui_forms.py` : dialogues créés (`ProgressBarDialog`, `BDConfigForm`, `SeriesForm`, `DirectScrape`), mais les événements/configurations ne sont pas encore branchés.
- `BDbaseScraper.py` : logique d’origine toujours présente, il doit devenir un orchestrateur minimal (
  import `scraper`, `settings`, `ui_forms` + exposer les hooks ComicRack).

---

## 🎯 Stratégie de finalisation

### 1. Assurer le moteur de scraping
- Compléter `BD_start()` pour qu’il boucle sur les livres, invoque `parseSerieInfo()`, puis `parseAlbumInfo()`/`parseRevueInfo()` selon la nature du lien.
- Exposer `QuickScrapeBDbase()` comme façade qui appelle `scraper.BD_start()` (option `book` + `cLink`).
- Ajouter l’actualisation `SeriesForm`/`ProgressBarDialog` dans la chaîne de décision (remplacer les appels directs aux dialogues dans le fichier original).
- Tester `parseSerieInfo()`/`parseAlbumInfo()` avec quelques URL (révision manuelle des logs pour vérifier que `book.Number`, `Title`, `ISBN`, etc. sont remplis).

### 2. Stabiliser les helpers
- Implémenter `search_series()` + `find_best_match()` pour rechercher une série lorsque le `serieUrl` n’est pas déjà renseigné.
- Remplir `download_cover()` afin de récupérer la couverture via `og:image` (le flag `BDBASE_DISABLE_COVER` reste respecté).
- Ajouter `normalize_album_number()`/`is_oneshot()`/`extract_authors_from_html()` pour éviter duplication dans `scraper.py`.

### 3. Finaliser l’UI et les hooks
- Compléter les onglets de `BDConfigForm`, binding avec `settings.LoadSetting()/SaveSetting()`, et événements (`button_Click`, `AllowUserChoice`, `PopUpEditionForm`).
- Vérifier que `DirectScrape` et `SeriesForm` communiquent correctement (mettre à jour `NewLink`, `NewSeries`).
- Recréer `BDbaseScraper.py` comme pont : importer `scraper`, `settings`, `ui_forms`, gérer les hooks `@Hook Books`, `@Hook ConfigScript`, etc.
- Ajouter le support `settings.get_plugin_path()` pour les assets (icônes, App.Config) dans la nouvelle structure.

---

## 💻 Méthode de travail

1. **Localiser** le code original dans `src/BDbaseScraper.py`. Les numéros de ligne figurent dans les sections précédentes de ce guide.
2. **Copier-coller** la portion ciblée dans le module correspondant (`scraper.py`, `ui_forms.py`).
3. **Adapter** les imports : utiliser `config.*`, `utils.*`, `settings.*` au lieu des variables globales.
4. **Réduire** la surface restante dans `BDbaseScraper.py` : ne garder que le hook + l’import du package refactoré.
5. **Tester** localement : `python -m py_compile src/bdbase_scraper/scraper.py`, puis lancer le plugin dans ComicRack.

---

## 📝 Checklist d'implémentation (statuts mis à jour)

### scraper.py
- [x] `parseAlbumInfo_bdbase()` – parsing complet des métadonnées
- [x] `parseSerieInfo()` – parsing série, albums et revues
- [x] `parseAlbumInfo()` – wrapper avec `_read_url`
- [x] `BD_start()` – boucle principale implémentée
- [x] `AlbumChooser()` – porté
- [x] `parseRevueInfo()` – porté
- [x] `download_cover()` – helper ajouté et utilisé
- [x] `SetAlbumInformation()` – porté
- [x] `search_series()` – helper fonctionnel
- [x] `find_best_match()` – helper fonctionnel
- [x] `normalize_album_number()` – helper fonctionnel
- [x] `extract_authors_from_html()` – helper fonctionnel

### ui_forms.py
- [ ] `BDConfigForm` – il faut achever les onglets et `button_Click`
- [ ] `ProgressBarDialog.Update()` – afficher progress bar et bouton cancel
- [ ] `SeriesForm` – tester et lier au workflow `AlbumChooser`
- [ ] `DirectScrape` – tester et connecter à `QuickScrapeBDbase`

### Intégration & tests
- [ ] Refactorer `BDbaseScraper.py` (Importer `scraper`, exposer les hooks)
- [ ] Connecter `ui_forms.py` aux options (BDConfigForm, DirectScrape, ProgressBarDialog)
- [ ] Tester dans ComicRack (logs, couvertures, dialogues)

---

## 🎯 Objectif de la Phase 3

**Résultat attendu** : plugin ComicRack totalement fonctionnel via les nouveaux modules.

**Critères de succès** :
- `scraper.py` peut traiter séries/albums (séries, volumes, revues, HS, etc.) sans faire référence aux anciens globals.
- `ui_forms.py` expose les dialogues nécessaires et sauvegarde les options.
- `BDbaseScraper.py` ne contient plus la logique monolithique, uniquement les hooks.
- Les traductions et la configuration passent par `settings.py`.
- Les tests (py_compile + ComicRack) passent sans erreurs.

---

## 🚀 Démarrage rapide (tâche prioritaire)

**Tâche 1: connecter l'UI**
1. Lier `BDConfigForm`/`DirectScrape` aux fonctions `LoadSetting()`/`SaveSetting()` de `settings`.
2. Ajouter `SeriesForm` et `ProgressBarDialog` aux flux de `SetSerieId()`/`BD_start()` (dans `scraper.py`).
3. Vérifier les dialogues (Annuler, timeout, messages) fonctionnent comme dans l'original.

**Tâche 2: refactorer `BDbaseScraper.py`**
1. Réécrire le fichier pour importer `bdbase_scraper.scraper`, `settings` et `ui_forms`.
2. Exposer les hooks `@Hook Books` et `@Hook ConfigScript` en appelant `scraper.BD_start()` et `ui_forms.BDConfigForm`.
3. Supprimer la logique monolithique restante tout en gardant la compatibilité ComicRack.

---

**Besoin d’un coup de main ?**
- Utiliser `rg` pour retrouver les anciens blocs de code.
- Copier-coller les regex de `config.py` si nécessaire.
- Tester fréquemment : `python -m py_compile src/bdbase_scraper/*.py` et ouvrir ComicRack pour valider.
