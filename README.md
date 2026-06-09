# Bitdefender GravityZone — XSIAM Mock Server

Serveur de simulation Flask pour le Content Pack Cortex XSIAM **GravityZone** de Bitdefender. Reproduit fidèlement le protocole JSON-RPC 2.0 de l'API GravityZone pour permettre le test complet de l'intégration XSIAM sans accès à un tenant GravityZone réel.

Fait partie de l'écosystème [xsiam-shared-personas](https://github.com/JCourtemanche/xsiam-shared-personas) — les endpoints générés utilisent les mêmes utilisateurs Business Corp que les autres simulateurs XSIAM.

## Protocole simulé

| Aspect | Détail |
|--------|--------|
| **Auth** | HTTP Basic Auth — `username=api_key`, `password=""` (encodé base64 par XSIAM) |
| **Protocol** | JSON-RPC 2.0 via `POST /api/<version>/jsonrpc/<service>` |
| **Versions** | v1.0, v1.1, v1.2 (toutes acceptées) |
| **Seed data** | 8 endpoints, 25 incidents Business Corp pré-générés |

## Méthodes JSON-RPC implémentées (17 méthodes)

### Service `companies`
- `getCompanyDetails` — détails de la société (retourne `id` utilisé comme `parentId`)

### Service `network`
- `getEndpointsList` — liste paginée des endpoints (`page`, `perPage`)
- `getManagedEndpointDetails` — détails d'un endpoint (`endpointId`, options scan logs/users)
- `getTaskStatus` — statut d'une tâche async (`taskId`, `returnSubtasks:true`) — auto-complétion après 3s

### Service `incidents`
- `getIncidentsList` — liste paginée des incidents (`filters`, `page`, `perPage`)
- `getIncident` — détail d'un incident (`id`)
- `updateIncidentNote` — ajouter une note (`incidentId`, `note`)
- `changeIncidentStatus` — changer le statut (`incidentId`, `status` int: 1=open, 2=in_progress, 3=closed, 4=false_positive)
- `createIsolateEndpointTask` — isoler un endpoint (type=16)
- `createRestoreEndpointFromIsolationTask` — dé-isoler un endpoint (type=17)

### Service `investigation`
- `startRetrieveInvestigationFileFromEndpoint` — démarrer un téléchargement de fichier
- `startCommandExecutionOnEndpoint` — exécuter une commande
- `killProcess` — tuer un processus (type=21)
- `collectInvestigationPackage` — collecter un package d'investigation
- `getInvestigationFileUrl` — statut d'une activité (auto-complétion après 3s)

### Service `internal`
- `runPredefinedLiveSearchQuery` — recherche live par hash (`QUERY_PROCESS_PER_HASH`, `QUERY_RUNNING_HASH`)
- `getLiveSearchQueryTaskResult` — résultats de la recherche live

### Endpoints REST (fichiers)
- `POST /storage/<bucket>` — upload d'un fichier (multipart/form-data)
- `GET /storage/<bucket>/<filename>` — téléchargement d'un ZIP d'investigation factice

## Démarrage local

```bash
cd simulator
pip install -r requirements.txt
python app.py
```

## Tests de validation

### 1. Auth valide (200)

```bash
# GravityZone encode l'API key en Basic Auth (username=api_key, password="")
curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getCompanyDetails","params":{},"id":1}' \
  http://localhost:8080/api/v1.0/jsonrpc/companies | python3 -m json.tool
```

### 2. Auth invalide (401)

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getCompanyDetails","params":{},"id":1}' \
  http://localhost:8080/api/v1.0/jsonrpc/companies
# → 401
```

### 3. Liste des incidents

```bash
curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getIncidentsList","params":{"page":1,"perPage":5,"options":{"includeChildCompanies":true}},"id":1}' \
  http://localhost:8080/api/v1.2/jsonrpc/incidents | python3 -m json.tool
```

### 4. Liste des endpoints

```bash
curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getEndpointsList","params":{"parentId":"gz-company-001","page":1,"perPage":100},"id":1}' \
  http://localhost:8080/api/v1.0/jsonrpc/network | python3 -m json.tool
```

### 5. Isoler un endpoint (tâche async)

```bash
# Récupérer l'ID du premier endpoint
EP_ID=$(curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"getEndpointsList","params":{"parentId":"gz-company-001","page":1,"perPage":1},"id":1}' \
  http://localhost:8080/api/v1.0/jsonrpc/network | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['items'][0]['id'])")

# Isoler
TASK=$(curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"createIsolateEndpointTask\",\"params\":{\"endpointId\":\"$EP_ID\"},\"id\":1}" \
  http://localhost:8080/api/v1.1/jsonrpc/incidents | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['taskId'])")

# Poller le statut (status=3 = processed, après ~3s)
sleep 4
curl -s -u 'my-api-key:' -X POST \
  -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"getTaskStatus\",\"params\":{\"taskId\":\"$TASK\",\"options\":{\"returnSubtasks\":true}},\"id\":1}" \
  http://localhost:8080/api/v1.1/jsonrpc/network | python3 -m json.tool
```

## Déploiement Cloud Run

```bash
# Pré-requis : gcloud configuré avec un projet GCP
bash deploy-cloudrun.sh
```

## Configuration XSIAM

Dans l'intégration XSIAM GravityZone, configurer :

| Champ | Valeur |
|-------|--------|
| **Server URL** | `http://localhost:8080` (local) ou URL Cloud Run |
| **API Key** | n'importe quelle valeur non-vide (ex: `mock-api-key`) |
| **Fetch incidents** | activé |

## Champs incidents (mappés vers XSIAM)

Tous les champs requis par l'intégration XSIAM sont présents dans les incidents générés :

| Champ GravityZone | Champ XSIAM | Layout |
|-------------------|-------------|--------|
| `incidentId` | `gravityzoneincidentid` | EDR + XDR |
| `incidentNumber` | `gravityzoneincidentnumber` | EDR + XDR |
| `incidentType` | `gravityzoneincidenttype` | EDR + XDR |
| `severityScore` | `gravityzoneincidentseverityscore` | EDR + XDR |
| `priority` | `gravityzoneincidentpriority` | EDR + XDR |
| `mainAction` | `gravityzoneincidentactiontaken` | EDR + XDR |
| `incidentLink` | `gravityzoneincidentlink` | EDR + XDR |
| `assignee.userId` | `gravityzoneincidentassigneduserid` | EDR + XDR |
| `company.id` | `gravityzonecompanyid` | EDR + XDR |
| `company.name` | `gravityzonecompanyname` | EDR + XDR |
| `details.computerId` | `gravityzonecomputerid` | EDR seul |
| `details.computerName` | `gravityzonecomputername` | EDR seul |
| `details.computerIp` | `gravityzonecomputerip` | EDR seul |
| `details.computerFqdn` | `gravityzonecomputerfqdn` | EDR seul |

## Structure du projet

```
simulator/
├── app.py                         # Flask app factory
├── auth.py                        # require_basic_auth (API key comme username)
├── config.py                      # Config (env vars)
├── requirements.txt
├── generators/
│   ├── base.py                    # Helpers + personas Business Corp
│   ├── endpoints.py               # Générateur d'endpoints GravityZone
│   ├── incidents.py               # Générateur d'incidents (EDR + XDR)
│   └── tasks.py                   # Machine à états async (isolate, investigation…)
└── routes/
    ├── jsonrpc.py                  # Dispatcher JSON-RPC 2.0 (17 méthodes)
    └── storage.py                  # Upload/download fichiers investigation
deployment/
├── Dockerfile
└── app.yaml
cloudbuild.yaml
deploy-cloudrun.sh
```
