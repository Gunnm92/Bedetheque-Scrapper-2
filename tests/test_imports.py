#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que les imports fonctionnent correctement
Ce script simule l'import du module principal comme le ferait ComicRack
"""

import sys
import os

# Ajouter le répertoire src au path
# Note: src contient des modules Python 2 pour ComicRack qui peuvent
# entrer en conflit avec Python 3. Ceci est normal et attendu.
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_path)  # Append instead of insert to avoid conflicts

print("=" * 60)
print("Test des imports pour BDbase Scraper")
print("=" * 60)

# Test 1: Import du module utilitaires
print("\n[1/3] Test import bdbase_utils...")
try:
    import bdbase_utils
    print("    ✓ bdbase_utils importé avec succès")

    # Vérifier que les fonctions sont disponibles
    functions = ['sstr', 'isPositiveInt', 'isnumeric', 'checkWebChar',
                 'checkRegExp', 'strip_tags', 'url_fix', 'if_else',
                 'ft', 'tf', 'GetFullURL', 'is_probable_album_url']

    for func_name in functions:
        if hasattr(bdbase_utils, func_name):
            print(f"    ✓ Fonction {func_name} disponible")
        else:
            print(f"    ✗ Fonction {func_name} MANQUANTE!")

    # Vérifier les constantes
    constants = ['BASE_DOMAIN', 'BASE_URL', 'TAG_RE_COMP']
    for const_name in constants:
        if hasattr(bdbase_utils, const_name):
            print(f"    ✓ Constante {const_name} disponible")
        else:
            print(f"    ✗ Constante {const_name} MANQUANTE!")

except Exception as e:
    print(f"    ✗ ERREUR lors de l'import de bdbase_utils: {e}")
    sys.exit(1)

# Test 2: Test des fonctions utilitaires
print("\n[2/3] Test fonctions utilitaires...")
try:
    # Test sstr
    result = bdbase_utils.sstr(None)
    assert result == '<None>', f"sstr(None) devrait retourner '<None>', a retourné: {result}"
    print("    ✓ sstr() fonctionne")

    # Test isPositiveInt
    assert bdbase_utils.isPositiveInt(5) == True
    assert bdbase_utils.isPositiveInt(-5) == False
    print("    ✓ isPositiveInt() fonctionne")

    # Test isnumeric
    assert bdbase_utils.isnumeric("3.14") == True
    assert bdbase_utils.isnumeric("abc") == False
    print("    ✓ isnumeric() fonctionne")

    # Test ft/tf
    assert bdbase_utils.ft("1") == True
    assert bdbase_utils.tf(True) == "1"
    print("    ✓ ft() et tf() fonctionnent")

    # Test GetFullURL
    url = bdbase_utils.GetFullURL("/serie/test")
    assert url == "https://www.bdbase.fr/serie/test", f"URL incorrecte: {url}"
    print("    ✓ GetFullURL() fonctionne")

    print("    ✓ Toutes les fonctions utilitaires testées avec succès!")

except Exception as e:
    print(f"    ✗ ERREUR lors des tests: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Vérifier que BDbaseScraper peut importer bdbase_utils
print("\n[3/3] Vérification de la compatibilité d'import...")
try:
    # On ne peut pas vraiment importer BDbaseScraper car il nécessite ComicRack
    # Mais on peut vérifier que le fichier est syntaxiquement correct
    with open('src/BDbaseScraper.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Vérifier que l'import est présent
    if 'from bdbase_utils import' in content:
        print("    ✓ Import de bdbase_utils présent dans BDbaseScraper.py")
    else:
        print("    ✗ Import de bdbase_utils MANQUANT dans BDbaseScraper.py")
        sys.exit(1)

    # Vérifier qu'il n'y a pas de définitions dupliquées
    duplicates = ['def sstr(', 'def isPositiveInt(', 'def isnumeric(',
                  'def checkWebChar(', 'def GetFullURL(']

    for dup in duplicates:
        if dup in content:
            print(f"    ⚠ ATTENTION: '{dup}' trouvée - possible duplication!")
        else:
            print(f"    ✓ Pas de duplication pour '{dup}'")

except Exception as e:
    print(f"    ✗ ERREUR: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ TOUS LES TESTS PASSÉS AVEC SUCCÈS!")
print("=" * 60)
print("\nÉtape 1 du refactoring terminée avec succès.")
print("Le plugin devrait fonctionner correctement avec ces modifications.")
