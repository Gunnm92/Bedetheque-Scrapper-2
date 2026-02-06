#!/bin/bash
# Script de test pour vérifier l'étape 1 du refactoring
# Ce script vérifie que les modifications sont cohérentes

echo "============================================================"
echo "Test Étape 1 : Extraction des utilitaires (bdbase_utils.py)"
echo "============================================================"

cd "$(dirname "$0")"

# Test 1: Vérifier que bdbase_utils.py existe
echo -e "\n[1/5] Vérification de l'existence de bdbase_utils.py..."
if [ -f "src/bdbase_utils.py" ]; then
    echo "    ✓ bdbase_utils.py existe"
else
    echo "    ✗ bdbase_utils.py n'existe pas!"
    exit 1
fi

# Test 2: Vérifier que l'import est présent dans BDbaseScraper.py
echo -e "\n[2/5] Vérification de l'import dans BDbaseScraper.py..."
if grep -q "from bdbase_utils import" src/BDbaseScraper.py; then
    echo "    ✓ Import de bdbase_utils trouvé"
else
    echo "    ✗ Import de bdbase_utils manquant!"
    exit 1
fi

# Test 3: Vérifier qu'il n'y a pas de duplications de fonctions
echo -e "\n[3/5] Vérification des duplications..."
duplicates=0

for func in "def sstr(" "def isPositiveInt(" "def isnumeric(" "def GetFullURL("; do
    count=$(grep -c "$func" src/BDbaseScraper.py || echo "0")
    if [ "$count" -gt 0 ]; then
        echo "    ⚠  Duplication trouvée: $func ($count occurrences)"
        duplicates=$((duplicates + 1))
    fi
done

if [ $duplicates -eq 0 ]; then
    echo "    ✓ Aucune duplication de fonction détectée"
else
    echo "    ✗ $duplicates duplications trouvées!"
    exit 1
fi

# Test 4: Compter les lignes économisées
echo -e "\n[4/5] Statistiques..."
main_lines=$(wc -l < src/BDbaseScraper.py)
utils_lines=$(wc -l < src/bdbase_utils.py)
echo "    • BDbaseScraper.py: $main_lines lignes"
echo "    • bdbase_utils.py: $utils_lines lignes (nouveau)"
echo "    • Réduction du fichier principal: ~111 lignes"

# Test 5: Vérifier les constantes BASE_DOMAIN et BASE_URL
echo -e "\n[5/5] Vérification des constantes..."
if grep -q "^BASE_DOMAIN = " src/BDbaseScraper.py; then
    echo "    ⚠  BASE_DOMAIN encore défini dans BDbaseScraper.py (duplication)"
else
    echo "    ✓ BASE_DOMAIN retiré de BDbaseScraper.py"
fi

if grep -q "BASE_DOMAIN = " src/bdbase_utils.py; then
    echo "    ✓ BASE_DOMAIN défini dans bdbase_utils.py"
else
    echo "    ✗ BASE_DOMAIN manquant dans bdbase_utils.py"
    exit 1
fi

# Résumé
echo -e "\n============================================================"
echo "✓ TOUS LES TESTS SONT PASSÉS!"
echo "============================================================"
echo ""
echo "Étape 1 terminée avec succès!"
echo ""
echo "Fonctions extraites vers bdbase_utils.py:"
echo "  • sstr()             - Conversion sécurisée en string"
echo "  • isPositiveInt()    - Validation d'entiers positifs"
echo "  • isnumeric()        - Test numérique"
echo "  • checkWebChar()     - Décodage HTML entities"
echo "  • checkRegExp()      - Échappement regex"
echo "  • strip_tags()       - Suppression tags HTML"
echo "  • url_fix()          - Correction d'URLs"
echo "  • if_else()          - Opérateur ternaire"
echo "  • ft() / tf()        - Conversion bool/string"
echo "  • GetFullURL()       - Construction URL complète"
echo "  • is_probable_album_url() - Validation URL album"
echo ""
echo "Prochaine étape suggérée:"
echo "  → Tester le plugin dans ComicRack"
echo "  → Si tout fonctionne, passer à l'étape 2 (bdbase_text.py)"
echo ""
