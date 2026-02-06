# 🔧 Guide d'Implémentation - Phase 3

**Date**: 2026-02-06  
**Phase**: 3 – Implémentation finale (intégration UI + hooks)  
**Objectif**: boucler les helpers, raccorder les dialogues au moteur de scraping et valider la chaîne BDbase complète avant les tests de Phase 4.

---

## 📋 État actuel

### ✅ Modules stabilisés
- `config.py`, `utils.py`, `settings.py` sont livrés : constantes/flags (cookies, patterns, messages), helpers HTTP/texte/logging et la gestion XML/traductions + `get_plugin_path()` pour les ressources.
- `scraper.py` héberge désormais toute la logique de parsing (séries, albums, revues, choix utilisateur) et expose les entrées `BD_start()` + `QuickScrapeBDbase()`. Les dialogues `ProgressBarDialog`, `SeriesForm` et `DirectScrape` sont invoqués depuis le module pour respecter les comportements historiques (annulation, timers, choix d’édition, logs).
- `ui_forms.py` contient l’ossature des dialogues (config, série, progress, quick scrape, HighDpiHelper) : les contrôles existent mais restent à remplir/brancher avec les options.
- `src/BDbaseScraper.py` est réduit à un orchestrateur : il importe `scraper`, `settings`, `ui_forms`, expose les hooks `Books`, `Editor`, `Library`, `ConfigScript` et délègue le travail à `QuickScrapeBDbase()` et `BDConfigForm`.

### 🔍 Points critiques à traiter
- **Helpers manquants** : `search_series()`, `find_best_match()`, `download_cover()`, `extract_authors_from_html()`, `normalize_album_number()`/`is_oneshot()` contiennent encore des TODO ou ne sont pas reliés aux champs `SetAlbumInformation`. Ils doivent utiliser les regex (`SERIE_LIST_PATTERN`, `BDBASE_ALBUM_AUTHOR`) définies dans `config.py`.
- **UI incomplète** : `BDConfigForm` n’affiche qu’une coquille d’onglets sans les contrôles métiers, et `ProgressBarDialog` ne gère pas encore le statut, les labels détaillés ni l’annulation (`scraper.bStopit`). `SeriesForm`/`DirectScrape` doivent confirmer leur communication avec `scraper.NewLink`, `NewSeries`, `TimerExpired` et les options `AllowUserChoice`/`TIMEPOPUP`.
- **Intégration & persistance** : les événements (`button_Click`, `AllowUserChoice`, `PopUpEditionForm`, `SaveSetting`) doivent rappeler `settings.LoadSetting()`/`SaveSetting()` pour conserver les préférences (nom de dossier, couverture, logs, timeout, etc.).

---

## 🎯 Plan de finalisation

### 1. Finaliser le moteur `scraper.py`
1. **BD_start / QuickScrape** – compléter la boucle de traitement pour utiliser `SeriesForm`, `ProgressBarDialog` et `DirectScrape` comme dans l’ancien fichier : vérifier que `books` passe bien du `BD_start()` ComicRack à `WorkerThread`, que `serieUrl` est normalisé (`__10000.html`), et que les logs renvoient les renommages/ignores.
2. **Helpers de recherche** – parsez `search_series()` avec `config.SERIE_LIST_PATTERN` pour retourner `(url, titre)` ; `find_best_match()` doit normaliser (`normalize_text`) et comparer les titres pour éviter des choix arbitraires (penser à `REMOVE_ARTICLES` et aux variantes de casse). Ces résultats alimenteront `SetSerieId()` quand `serieUrl` est vide.
3. **Couverture & auteurs** – `download_cover()` doit réutiliser `ComicRack.App.SetCustomBookThumbnail`, respecter `CBCover`/`BDBASE_DISABLE_COVER` et fermer les streams. `extract_authors_from_html()` doit employer `BDBASE_ALBUM_AUTHOR` pour peupler les rôles (Writer, Penciller, etc.) et alimenter `SetAlbumInformation`.
4. **Numérotation & one-shots** – `normalize_album_number()` et `is_oneshot()` servent `parseAlbumInfo()` ; assurez-vous qu’ils gèrent les formats `1`, `1.5`, `HS`, `1a`, `One shot` et qu’ils alimentent `book.Number`, `book.AlternateNumber`, `book.Format`.
5. **Refactorer les doublons** – nettoyez les définitions en double (ex. `download_cover`) pour éviter d’avoir des versions en conflit.

### 2. Compléter les interfaces (`ui_forms.py`)
1. **ProgressBarDialog** – ajouter les labels / images (couverture si disponible), illustrer l’état courant et brancher le bouton Annuler pour mettre `scraper.bStopit = True`. `Update()` doit gérer les incréments et la désactivation quand `current == total`.
2. **BDConfigForm** – recréer les trois onglets (Général, Champs, Debug) avec les contrôles (checkboxes, textboxes, radio) tirés de `config.*`/`settings.*`. Chaque contrôle doit préremplir sa valeur grâce à `settings.LoadSetting()` et appeler `SaveSetting()` dans `button_Click`. Ne pas oublier les `Trans(index)` pour les libellés et `HighDpiHelper`.
3. **SeriesForm & DirectScrape** – confirmer que `SeriesForm` alimente `scraper.NewLink`, `NewSeries` et respecte `config.AllowUserChoice`. `DirectScrape` doit valider l’URL, activer `scraper.LinkBDbase` et accepter les raccourcis clavier (`KeyPreview`). Le timer `TimerExpired` doit être réinitialisé (`False`) avant chaque appel.
4. **Options + événements** – `AllowUserChoice`, `TIMEPOPUP`, `PopUpEditionForm`, `HighDpiHelper` et `FormType` doivent être utilisés pour reproduire les comportements originaux, notamment l’expiration automatique et la sélection forcée.

### 3. Hooks et configuration
1. **BDbaseScraper.py** – conserver les hooks `Books`, `Editor`, `Library` et `ConfigScript`, appeler `QuickScrapeBDbase()`/`ConfigureBDbaseQuick()` et garantir que `settings.LoadSetting()` est invoqué avant d’afficher un formulaire.
2. **Assets** – `settings.get_plugin_path()` doit pointer vers `src/assets` pour que les icônes (`BDbase.ico`, `BDbaseQ.png`) fonctionnent dans les dialogues.
3. **Traductions** – les `Trans(index)` restent la passerelle vers les textes localisés ; assurez-vous que tous les formulaires les utilisent et que `settings.Translate()` est appelé dès l’initialisation.

### 4. Tests et validation
1. `python -m py_compile src/*.py` pour attraper les erreurs de syntaxe avant de lancer ComicRack.
2. Ouvrir ComicRack Community Edition, charger le plugin et :
   - lancer un QuickScrape (sélection manuelle + `DirectScrape`) et vérifier que `SerieForm` et `ProgressBarDialog` s’ouvrent, que les logs renvoient les renoms/ignores, que la couverture se télécharge et qu’il est possible d’annuler.
   - ouvrir le ConfigScript, modifier une option (ex : `CBCover`), valider et relancer pour confirmer que `settings` persiste les changements.
   - déclencher un rescrape avec `BD_start()` et contrôler que `NewLink`, `SerieUrl`, `FindSeries` s’alignent.
3. Vérifier `BDbase_Rename_Log.txt` / `BDbase_debug_log.txt` sont créés dans le dossier de script et s’ouvrent depuis les boîtes de dialogue (via `MessageBox`).

---

## 📌 Ressources complémentaires
- `src/BDbaseScraper.py` : référence pour la nouvelle entrée ComicRack qui expose les hooks.
- `src/config.py` : patterns regex, options, booléens (CBCover, CBSeries, TIMEPOPUP, etc.).
- `src/settings.py` : traduction (`Trans`), chargement/enregistrement XML (`LoadSetting`, `SaveSetting`), `get_plugin_path()`.
- `src/utils.py` : fonctions utilitaires (`debuglog`, `titlize`, `strip_tags`, `normalize_text`, etc.) à réutiliser dans les helpers.

**Besoin d’un coup de main ?** Lancer `rg -n 'serieUrl' -n 'Trans'` pour retrouver l’usage historique dans `src/BDbaseScraper.py` ou l’ancien plugin `release\BDbaseScraper`. Conserver les logs (`log_BD`, `SeriesForm`, `DirectScrape`) identiques garantit la transition.
