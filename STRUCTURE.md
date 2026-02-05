# 📁 Structure du Projet BDbase Scraper

## Vue d'ensemble de la nouvelle organisation

```
bdbasescraper/
│
├── 📄 REFACTORING_PLAN.md          Plan du refactoring
├── 📄 STRUCTURE.md                 Ce fichier (vue d'ensemble)
├── 📄 PROGRESS.md                  Suivi de progression
├── 📄 IMPLEMENTATION_GUIDE.md      Guide de phase 3
├── 📄 FINAL_SUMMARY.md             Résumé final (en cours)
│
├── 📂 release/                     Build du plugin
│   └── BDbase Scraper_v1.00.crplugin
│
└── 📂 src/
    ├── 📄 README.md                Documentation source
    ├── 📄 BDbaseScraper.py         Point d'entrée original (à refactorer)
    ├── 📄 BDTranslations.Config    Traductions FR/EN
    ├── 📄 Package.ini              Configuration ComicRack
    │
    ├── 📂 bdbase_scraper/          ✨ Package refactoré
    │   ├── __init__.py             Initialisation
    │   ├── config.py               Constantes / patterns ✅
    │   ├── utils.py                Helpers ✅
    │   ├── settings.py             Config + traductions ✅
    │   ├── scraper.py              Parsing + sélection ⚠️ (entry point en cours)
    │   └── ui_forms.py             Dialogues ⚠️ (events à brancher)
    │
    ├── 📂 stdlib/                  Python 2.7 stdlib (29 fichiers)
    └── 📂 assets/                  Ressources graphiques (6 fichiers)
```

## 🧭 Statuts des modules

| Module | Status | Notes |
|--------|--------|-------|
| `config.py` | ✅ | Constantes et flags migrés. |
| `utils.py` | ✅ | Helpers complet pour texte / http / logging. |
| `settings.py` | ✅ | Gestion App.Config + traductions. |
| `scraper.py` | ⚠️ | Parsing/albums/revues portés ; `BD_start`, `QuickScrape` et helpers manquent. |
| `ui_forms.py` | ⚠️ | Dialogues créés, ils doivent encore être liés aux événements et à `settings`. |
| `BDbaseScraper.py` | ⚠️ | Ancienne logique monolithique – doit devenir un orchestrateur minimal. |

---

## 🔄 Progression du refactoring

### Phase 1: Infrastructure
- ✅ Branches / dossiers créés
- ✅ `config.py`, `utils.py`, `settings.py`
- ✅ Documentation (plan, structure, guide)

### Phase 2: Modules métier
- ✅ `scraper.py` structure (parsing, albums, revues)
- ⚠️ `BD_start`, `QuickScrape`, helpers encore à écrire
- ⚠️ `ui_forms.py` - événements et liaison à finaliser

### Phase 3: Intégration & tests (en cours)
- Actions restantes : réécrire `BDbaseScraper.py`, exposer les hooks, brancher l’UI, tester dans ComicRack.

---

## 🎯 Avantages de la nouvelle structure
- ✅ **Lisibilité** : chaque rôle a son module
- ✅ **Maintenance** : plus facile d’ajouter de nouvelles traductions ou patterns
- ✅ **Tests** : `scraper.py` peut être compilé/testé indépendamment
- ✅ **Documentation** : guide, plan, progrès, summary alignés

---

## 📝 Notes importantes
1. **Variables globales** comme `dlgNumber` sont désormais limitées à `scraper.py`.
2. **Accès aux ressources** doit passer par `settings.get_plugin_path()` (utile pour `App.Config`, icônes, translations).
3. **Compatibilité ComicRack** : conserver les décorateurs `@Hook` et l’import `cYo.Projects.ComicRack.Engine` dans `BDbaseScraper.py` (lors de la réécriture finale).

---

**Date de mise à jour**: 2026-02-05 23:58
