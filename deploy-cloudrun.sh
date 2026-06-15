#!/bin/bash
# Déploie le mock server GravityZone sur Cloud Run avec gestion IAM automatisée.
# Usage: bash deploy-cloudrun.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Variables de base ---
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
CURRENT_USER=$(gcloud config get-value account 2>/dev/null)
# Récupération du numéro de projet pour déduire le compte de service Compute
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)" 2>/dev/null)
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

REGION="europe-west1"
SERVICE_NAME="gravityzone-mock"
REPO_NAME="gravityzone-mock"

echo -e "${GREEN}=== Déploiement Cloud Run - $SERVICE_NAME ===${NC}\n"
echo -e "${YELLOW}Project ID:${NC}     $PROJECT_ID"
echo -e "${YELLOW}User:${NC}           $CURRENT_USER"
echo -e "${YELLOW}Compute SA:${NC}     $COMPUTE_SA"
echo -e "${YELLOW}Region:${NC}         $REGION"
echo -e "${YELLOW}Service:${NC}        $SERVICE_NAME"
echo ""

echo -e "${YELLOW}[0/6] Configuration des permissions IAM...${NC}"

echo "  -> Configuration des droits pour ton utilisateur ($CURRENT_USER)"
for ROLE in "roles/cloudbuild.builds.editor" "roles/storage.objectAdmin" "roles/run.admin" "roles/iam.serviceAccountUser"; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="$ROLE" \
    --condition=None \
    --quiet > /dev/null
done

echo "  -> Configuration des droits pour Cloud Build ($COMPUTE_SA)"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$COMPUTE_SA" \
  --role="roles/storage.objectAdmin" \
  --condition=None \
  --quiet > /dev/null

echo -e "${GREEN}✓ Permissions IAM appliquées (pause de 10
