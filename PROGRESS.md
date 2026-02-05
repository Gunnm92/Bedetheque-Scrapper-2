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
- **scraper.py** – parsing + workflows portés (parseSerieInfo, parseAlbumInfo*, parseRevueInfo, AlbumChooser, SetAlbumInformation). `BD_start()`/`QuickScrapeBDbase()` fonctionnent dans le module et les helpers (`search_series`, `find_best_match`, `normalize_album_number`, `download_cover`, `extract_authors_from_html`) sont implémentés ; reste la liaison UI/entry.
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
1. Connecter `BDConfigForm`, `SeriesForm` et `ProgressBarDialog` aux options `settings` afin que `scraper.BD_start()` puisse afficher les dialogues comme avant.
2. Finaliser `BDbaseScraper.py` pour qu’il importe `bdbase_scraper` et expose les hooks ComicRack (Books, ConfigScript, QuickScrape).
3. Tester le plugin dans ComicRack, vérifier les logs, les couvertures, les dialogues et le quick scrape.


---

## 🔁 Prochaine phase
- **Phase 3 (Intégration)** : Connecter l’UI (`BDConfigForm`, `SeriesForm`, `ProgressBarDialog`), refaire `BDbaseScraper.py` et valider les hooks + quick scrape.
- **Phase 4 (Tests)** : Tester dans ComicRack (logs, couvertures, options, QuickScrape).
- **Phase 5 (Finalisation)** : Mise à jour doc finale et merge vers `main`.

---

**Dernière mise à jour**: 2026-02-05 23:58
