# 📈 Progression du Refactoring

**Branche**: `refactoring/split-main-file`
**Début**: 2026-02-05
**Status**: Phase 2 → Phase 3 (intégration en cours)

---

## 🎯 Objectif général
Refactorer le monolithe `BDbaseScraper.py` en modules clairs (`config`, `utils`, `settings`, `scraper`, `ui_forms`) tout en gardant le plugin compatible ComicRack.

---

## ✅ Modules livrés
1. **config.py** (200 lignes) – Constantes, flags, expressions régulières, cookie container.
2. **utils.py** (400 lignes) – Helpers HTTP, texte, logging, parsing et formats partagés.
3. **settings.py** (220 lignes) – Chargement/sauvegarde XML, traduction, `get_plugin_path()`.

---

## ⚠️ Modules en cours
- **scraper.py** – `parseSerieInfo`, `parseAlbumInfo`, `parseAlbumInfo_bdbase`, `AlbumChooser`, `parseRevueInfo`, `SetAlbumInformation` importés. `BD_start()`, `QuickScrapeBDbase()` et les helpers (`search_series`, `normalize_album_number`, `download_cover`, `extract_authors_from_html`) restent à terminer.
- **ui_forms.py** – Dialogues (`BDConfigForm`, `ProgressBarDialog`, `SeriesForm`, `DirectScrape`, `HighDpiHelper`) créés, mais les événements et la liaison avec `settings` ne sont pas branchés.
- **BDbaseScraper.py** – Le fichier original est encore monolithique; il doit bientôt devenir le point d’entrée qui importe `bdbase_scraper` et expose les hooks.

---

## 📊 Progression chiffrée
```
✅ Modules configurés : 3/5 (config, utils, settings)
⚠️ Scraper : parsing + revue portés (~60%) mais entry point + helpers à écrire
⚠️ UI : structure en place, events et dialogues à connecter
📁 Structure projet : nouvelle hiérarchie + documentation mise à jour
```

---

## 🧭 Rappel du workflow à venir
1. Compléter `BD_start()` et `QuickScrapeBDbase()` pour déclencher le parsing (serie → album/revue).
2. Finaliser `search_series`, `find_best_match`, `normalize_album_number`, `download_cover`, `extract_authors_from_html`.
3. Lier `BDConfigForm` / `DirectScrape` aux `settings` (chargement / sauvegarde) et intégrer `SeriesForm`/`ProgressBarDialog`.
4. Refactorer `BDbaseScraper.py` pour qu’il importe `scraper`/`settings`/`ui_forms` et expose les hooks ComicRack (`@Hook Books`, `@Hook ConfigScript`).
5. Tester dans ComicRack (couverture, logs, dialogues, QuickScrape). 

---

## 🔁 Prochaine phase
- **Phase 3 (Intégration)** : Écrire les points d’entrée (`BD_start`, `QuickScrape`), lier l’UI et valider le fonctionnement complet.
- **Phase 4 (Tests)** : Tester avec ComicRack, vérifier les logs, couvertures, comportements d’annulation.
- **Phase 5 (Finalisation)** : Ajuster la documentation finale et préparer le merge vers `main`.

---

**Dernière mise à jour**: 2026-02-05 23:58
