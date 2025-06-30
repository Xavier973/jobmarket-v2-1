#!/bin/bash

# Script de transfert des fichiers JSON WTTJ vers la VM
# Auteur: JobMarket ETL Team
# Date: $(date +%Y-%m-%d)

# Configuration
LOCAL_WTTJ_DIR="/home/xadmin/projets/jobmarket-v2-1/data/raw/wttj"
VM_USER="ubuntu"
VM_IP="20.121.45.177"
VM_KEY_PATH="/home/xadmin/VM-Jobmarket-AZ-01_key.pem"
VM_REMOTE_DIR="/home/ubuntu/jobmarket-v2-1/data/raw/wttj"
TRANSFERRED_DIR="${LOCAL_WTTJ_DIR}/Transfered"
LOG_FILE="/home/xadmin/projets/jobmarket-v2-1/data/logs/wttj/wttj_transfert.log"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Créer le dossier de logs si nécessaire
mkdir -p "$(dirname "$LOG_FILE")"

# Fonction pour écrire dans le log (messages essentiels uniquement)
write_log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo "$message" >> "$LOG_FILE"
}

# Fonction pour afficher les messages (terminal uniquement)
log_message() {
    local message="$1"
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $message"
}

log_success() {
    local message="$1"
    echo -e "${GREEN}[SUCCESS]${NC} $message"
}

log_warning() {
    local message="$1"
    echo -e "${YELLOW}[WARNING]${NC} $message"
}

log_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message"
    write_log "[ERROR] $message"
}

# Vérification des prérequis
check_prerequisites() {
    log_message "Vérification des prérequis..."
    
    # Vérifier que le dossier source existe
    if [ ! -d "$LOCAL_WTTJ_DIR" ]; then
        log_error "Le dossier source $LOCAL_WTTJ_DIR n'existe pas"
        exit 1
    fi
    
    # Vérifier que la clé SSH existe
    if [ ! -f "$VM_KEY_PATH" ]; then
        log_error "La clé SSH $VM_KEY_PATH n'existe pas"
        exit 1
    fi
    
    # Vérifier que scp est disponible
    if ! command -v scp &> /dev/null; then
        log_error "La commande scp n'est pas disponible"
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Créer le dossier de sauvegarde si nécessaire
create_backup_directory() {
    if [ ! -d "$TRANSFERRED_DIR" ]; then
        log_message "Création du dossier de sauvegarde: $TRANSFERRED_DIR"
        mkdir -p "$TRANSFERRED_DIR"
        log_success "Dossier de sauvegarde créé"
    fi
}

# Transférer les fichiers JSON vers la VM
transfer_files_to_vm() {
    log_message "Recherche des fichiers JSON dans $LOCAL_WTTJ_DIR..."
    
    # Compter les fichiers JSON (excluant les sous-dossiers)
    json_files_count=$(find "$LOCAL_WTTJ_DIR" -maxdepth 1 -name "*.json" | wc -l)
    
    if [ "$json_files_count" -eq 0 ]; then
        log_warning "Aucun fichier JSON trouvé dans $LOCAL_WTTJ_DIR"
        return 0
    fi
    
    log_message "Transfert de $json_files_count fichier(s) JSON vers la VM..."
    
    # Lister les fichiers qui vont être transférés
    log_message "Fichiers à transférer :"
    for file in "$LOCAL_WTTJ_DIR"/*.json; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            filesize=$(du -h "$file" | cut -f1)
            log_message "  - $filename ($filesize)"
        fi
    done
    
    # Transférer tous les fichiers JSON vers la VM
    log_message "Exécution de la commande SCP..."
    scp -i "$VM_KEY_PATH" "$LOCAL_WTTJ_DIR"/*.json "$VM_USER@$VM_IP:$VM_REMOTE_DIR/"
    
    if [ $? -eq 0 ]; then
        log_success "Transfert vers la VM réussi"
        # Enregistrer les fichiers transférés dans le log
        for file in "$LOCAL_WTTJ_DIR"/*.json; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                filesize=$(du -h "$file" | cut -f1)
                write_log "Fichier transféré: $filename ($filesize)"
            fi
        done
        return 0
    else
        log_error "Échec du transfert vers la VM"
        return 1
    fi
}

# Déplacer les fichiers transférés vers le dossier de sauvegarde
move_transferred_files() {
    log_message "Déplacement des fichiers transférés vers $TRANSFERRED_DIR..."
    
    # Déplacer tous les fichiers JSON vers le dossier de sauvegarde
    for file in "$LOCAL_WTTJ_DIR"/*.json; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            log_message "Déplacement de $filename"
            mv "$file" "$TRANSFERRED_DIR/"
            if [ $? -eq 0 ]; then
                log_success "Fichier $filename déplacé avec succès"
            else
                log_error "Échec du déplacement de $filename"
            fi
        fi
    done
    
    log_success "Tous les fichiers ont été déplacés vers le dossier de sauvegarde"
}

# Afficher un résumé
show_summary() {
    log_message "=== RÉSUMÉ DU TRANSFERT ==="
    log_message "Fichiers transférés vers la VM: $VM_USER@$VM_IP:$VM_REMOTE_DIR/"
    log_message "Fichiers sauvegardés localement: $TRANSFERRED_DIR"
    
    # Compter les fichiers dans le dossier de sauvegarde
    backup_count=$(find "$TRANSFERRED_DIR" -name "*.json" | wc -l)
    log_message "Nombre de fichiers sauvegardés: $backup_count"
    
    # Lister les fichiers sauvegardés
    if [ "$backup_count" -gt 0 ]; then
        log_message "Fichiers sauvegardés :"
        for file in "$TRANSFERRED_DIR"/*.json; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                filesize=$(du -h "$file" | cut -f1)
                log_message "  - $filename ($filesize)"
            fi
        done
    fi
    
    log_success "Transfert terminé avec succès"
}

# Fonction principale
main() {
    # Séparateur pour une nouvelle exécution dans le log
    log_message "=========================================="
    log_message "NOUVELLE EXÉCUTION DU TRANSFERT WTTJ"
    log_message "=========================================="
    
    log_message "=== DÉBUT DU TRANSFERT WTTJ VERS LA VM ==="
    
    check_prerequisites
    create_backup_directory
    
    if transfer_files_to_vm; then
        move_transferred_files
        show_summary
    else
        log_error "Le transfert a échoué. Aucun fichier n'a été déplacé."
        exit 1
    fi
    
    log_message "=== FIN DU TRANSFERT ==="
    write_log "=========================================="
}

# Exécution du script
main "$@" 