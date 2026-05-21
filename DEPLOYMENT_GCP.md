# Guide de déploiement GCP — XSIAM Simulator Template

## Avant de déployer

1. **Personnalise `cloudbuild.yaml`** : remplace `MY_SERVICE` par ton nom de service
2. **Personnalise `deploy-cloudrun.sh`** : mets à jour `SERVICE_NAME`, `REPO_NAME`, et `--set-env-vars`
3. **Personnalise `deployment/app.yaml`** : mets à jour les variables d'environnement

## Déploiement rapide

```bash
gcloud auth login
gcloud config set project VOTRE_PROJECT_ID

bash deploy-cloudrun.sh
```

## Étapes manuelles

### 1. Activer les APIs

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Créer le repository Artifact Registry

```bash
gcloud artifacts repositories create MY_SERVICE \
  --repository-format=docker \
  --location=europe-west1
```

### 3. Build et push

```bash
gcloud builds submit --config cloudbuild.yaml
```

### 4. Déployer

```bash
IMAGE="europe-west1-docker.pkg.dev/$(gcloud config get-value project)/MY_SERVICE/MY_SERVICE:latest"

gcloud run deploy MY_SERVICE \
  --image $IMAGE \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars AUTH_API_KEY=change-me,DEBUG=False
```

## Validation

```bash
SERVICE_URL=$(gcloud run services describe MY_SERVICE \
  --region europe-west1 --format 'value(status.url)')

curl $SERVICE_URL/health
```

## Notes

- Le package `xsiam-shared-personas` est installé depuis GitHub pendant le build Docker — git est installé dans l'image pour cette raison
- `--min-instances 0` active le scale-to-zero pour réduire les coûts
