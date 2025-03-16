#!/bin/bash
# Script pour tous les fichiers JSON de raw/francetravail vers transformed/francetravail
# Définition des chemins
SOURCE_DIR="/app/data/raw/francetravail"
DEST_DIR="/app/data/transformed/francetravail"

# Vérification des dossiers
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Erreur: Dossier source $SOURCE_DIR non trouvé"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
    echo "Création du dossier destination $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

# Compteur de fichiers
total_files=$(ls -1 "$SOURCE_DIR"/*.json 2>/dev/null | wc -l)
current_file=0

echo "Début du traitement de $total_files fichiers..."

# Traitement de chaque fichier JSON
for file in "$SOURCE_DIR"/*.json; do
    if [ -f "$file" ]; then
        ((current_file++))
        echo "[$current_file/$total_files] Traitement de $(basename "$file")..."
        python data_cleaning_ft.py "$file" "$DEST_DIR"
    fi
done

echo "Traitement terminé!" 