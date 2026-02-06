# 🎯 Refactoring en cours - BDbase Scraper

**Date**: 2026-02-05
**Branche**: `refactoring/split-main-file`
**Status**: Phase 3 (Intégration) en cours

---

## 📌 Résumé exécutif
Le monolithe `src/BDbaseScraper.py` a été restructuré en modules plats (`config.py`, `utils.py`, `settings.py`, `scraper.py`, `ui_forms.py`) directement à la racine de `src/`. `scraper.py` contient désormais les fonctions de parsing (albums, séries, revues et sélection utilisateur) et `ui_forms.py` l’ossature des dialogues. Il reste à connecter `BD_start`, les helpers, l’UI et BDbaseScraper aux nouveaux modules.

---

## 🧩 Modules atteints
| Module | Statut | Avancement |
|--------|--------|------------|
| `config.py` | ✅ | Constantes, flags, regex, cookie container
| `utils.py` | ✅ | Helpers HTTP/texte/logging/parsing
| `settings.py` | ✅ | AppSettings + traductions + `get_plugin_path()`
| `scraper.py` | ⚠️ | Parsing complet (album/serie/revue), `BD_start` & `QuickScrape` à écrire, helpers manquants
| `ui_forms.py` | ⚠️ | Dialogues créés, événements + binding à `settings` à terminer
| `BDbaseScraper.py` | ⚠️ | Ancien fichier à refactorer en orchestrateur

---

## 🛠️ Travaux restants
1. Achever `BD_start()`/`QuickScrapeBDbase()` qui orchestrent l’appel à `parseSerieInfo()` puis `parseAlbumInfo()`.
2. Implémenter `search_series()`, `find_best_match()`, `normalize_album_number()`, `download_cover()` et `extract_authors_from_html()` dans `scraper.py`.
3. Lier `SeriesForm`, `ProgressBarDialog`, `BDConfigForm` et `DirectScrape` au nouveau `settings` + aux hooks existants (`AllowUserChoice`, `PopUpEditionForm`).
4. Réécrire `BDbaseScraper.py` en module léger qui importe `scraper`, `settings` et `ui_forms`, expose les hooks `@Hook Books` et `@Hook ConfigScript`, puis fait tourner `scraper.BD_start()`.
5. Tester l’ensemble dans ComicRack (logs, couvertures, rejets, QuickScrape) avant de passer la Phase 4.

---

## 📆 Prochaine phase
**Phase 3 (Intégration)** : terminer l’entrée `BD_start`, connecter l’UI, exposer les hooks et valider les options. Ensuite, Phase 4 (Tests) sera déclenchée une fois la chaîne fonctionnelle.

---

**Dernière mise à jour**: 2026-02-05 23:58
