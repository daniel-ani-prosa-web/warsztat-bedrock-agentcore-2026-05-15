#!/bin/bash
# Sprawdza czy srodowisko jest gotowe na warsztat.
# Uruchom: bash check-ready.sh

PASS=0
FAIL=0

check() {
    if eval "$2" > /dev/null 2>&1; then
        echo "  [OK]  $1"
        ((PASS++))
    else
        echo "  [FAIL] $1"
        ((FAIL++))
    fi
}

echo ""
echo "=== Sprawdzanie srodowiska ==="
echo ""

check "AWS CLI zainstalowane" "aws --version"
check "Git zainstalowany" "git --version"

# Python version check (3.10-3.13)
PYVER=$(python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+')
if [[ "$PYVER" =~ ^3\.(1[0-3])$ ]]; then
    echo "  [OK]  Python $PYVER (3.10-3.13)"
    ((PASS++))
elif [[ -n "$PYVER" ]]; then
    echo "  [FAIL] Python $PYVER — potrzebujesz 3.10-3.13 (nie 3.14+)"
    ((FAIL++))
else
    echo "  [FAIL] Python3 nie znaleziony"
    ((FAIL++))
fi

# AWS credentials
if aws sts get-caller-identity > /dev/null 2>&1; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    echo "  [OK]  AWS credentials (konto: $ACCOUNT)"
    ((PASS++))
else
    echo "  [FAIL] AWS credentials — ustaw AWS_PROFILE lub uruchom 'aws configure'"
    ((FAIL++))
fi

# Region
if [[ -n "$AWS_REGION" ]]; then
    echo "  [OK]  AWS_REGION=$AWS_REGION"
    ((PASS++))
elif [[ -n "$AWS_DEFAULT_REGION" ]]; then
    echo "  [OK]  AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION"
    ((PASS++))
else
    echo "  [FAIL] AWS_REGION nie ustawiony — export AWS_REGION=us-east-1"
    ((FAIL++))
fi

# zip (needed by prereq.sh)
check "zip zainstalowany" "zip --version"

# Optional
echo ""
echo "--- Opcjonalne ---"

if command -v uv > /dev/null 2>&1; then
    echo "  [OK]  uv ($(uv --version 2>/dev/null))"
else
    echo "  [--]  uv nie zainstalowany (opcjonalne, pip tez dziala)"
fi

if command -v docker > /dev/null 2>&1; then
    echo "  [OK]  Docker ($(docker --version 2>/dev/null | head -1))"
else
    echo "  [--]  Docker nie zainstalowany (opcjonalne — Lab 4 uzywa CodeBuild server-side)"
fi

echo ""
echo "=== Wynik: $PASS OK, $FAIL FAIL ==="
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo "Wszystko gotowe. Do zobaczenia na warsztacie!"
else
    echo "Napraw powyzsze bledy przed warsztatem."
    echo "Szczegoly: workshop/00-prerequisites.md"
fi
echo ""
