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
# Ajout des rôles pour le Storage, Artifact Registry et les Logs
for ROLE in "roles/storage.objectAdmin" "roles/artifactregistry.writer" "roles/logging.logWriter"; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="$ROLE" \
    --condition=None \
    --quiet > /dev/null
done

echo -e "${GREEN}✓ Permissions IAM appliquées (pause de 10s pour laisser les serveurs Google se synchroniser)${NC}\n"
sleep 10

echo -e "${YELLOW}[1/6] Activation des APIs...${NC}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com storage.googleapis.com
echo -e "${GREEN}✓ APIs activées${NC}\n"

echo -e "${YELLOW}[2/6] Configuration d'Artifact Registry...${NC}"
REPO_EXISTS=$(gcloud artifacts repositories list \
  --location=$REGION \
  --filter="name:$REPO_NAME" \
  --format="value(name)" 2>/dev/null)

if [ -z "$REPO_EXISTS" ]; then
  gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="$SERVICE_NAME images" \
    --quiet
  echo -e "${GREEN}✓ Repository créé${NC}"
else
  echo -e "${GREEN}✓ Repository existe déjà${NC}"
fi
echo ""

echo -e "${YELLOW}[3/6] Vérification du répertoire...${NC}"
if [ ! -f "deployment/Dockerfile" ]; then
  echo -e "${RED}ERREUR: Dockerfile non trouvé. Lancez ce script depuis la racine du projet.${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Dockerfile trouvé${NC}\n"

echo -e "${YELLOW}[4/6] Construction de l'image Docker...${NC}"
echo "Cela peut prendre 2-3 minutes..."
gcloud builds submit --config cloudbuild.yaml
IMAGE_PATH="${REGION}-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$REPO_NAME:latest"
echo -e "${GREEN}✓ Image construite: $IMAGE_PATH${NC}\n"

echo -e "${YELLOW}[5/6] Déploiement sur Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_PATH \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars="COMPANY_ID=gz-company-001,COMPANY_NAME=Business Corp,NUM_ENDPOINTS=8,NUM_INCIDENTS=25,DEBUG=False"

echo -e "${YELLOW}[6/6] Configuration de l'accès public...${NC}"
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT_ID \
  --quiet 2>/dev/null && PUBLIC_ACCESS=true || PUBLIC_ACCESS=false

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Déploiement réussi !${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}URL du service:${NC} ${GREEN}${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}Tests de validation (remplacer SERVER_URL):${NC}"
echo ""
echo "  # Health check"
echo "  curl ${SERVICE_URL}/health"
echo ""
echo "  # Obtenir la liste des incidents (Basic Auth : api_key comme username)"
echo "  curl -s -u 'MY_API_KEY:' -X POST \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"jsonrpc\":\"2.0\",\"method\":\"getIncidentsList\",\"params\":{\"page\":1,\"perPage\":5},\"id\":1}' \\"
echo "    ${SERVICE_URL}/api/v1.2/jsonrpc/incidents | python3 -m json.tool | head -40"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "  Voir les logs:  gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "  Supprimer:      gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""
