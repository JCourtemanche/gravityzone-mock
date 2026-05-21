# XSIAM Simulator Template

Template de départ pour créer un simulateur d'API pour Cortex XSIAM.

Utilise le package [xsiam-shared-personas](https://github.com/JCourtemanche/xsiam-shared-personas) pour que les mêmes utilisateurs, IPs et indicateurs de menace apparaissent de manière cohérente à travers tous les simulateurs dans XSIAM.

## Simulateurs existants basés sur ce template

| Projet | API simulée | GitHub |
|---|---|---|
| proofpoint-tap-simulator | ProofPoint TAP | [lien](https://github.com/JCourtemanche/proofpoint-tap-simulator) |
| sentinelone-simul | SentinelOne | [lien](https://github.com/JCourtemanche/sentinelone-simul) |
| cato-networks-simul | Cato Networks | [lien](https://github.com/JCourtemanche/cato-networks-simul) |

## Checklist de démarrage

### 1. Copier le template

```bash
# Cloner le template dans un nouveau dossier
git clone https://github.com/JCourtemanche/xsiam-simulator-template mon-nouveau-simul
cd mon-nouveau-simul

# Lier à ton nouveau repo GitHub
git remote set-url origin https://github.com/JCourtemanche/mon-nouveau-simul.git
```

### 2. Personnaliser les fichiers — dans cet ordre

| Fichier | Quoi changer |
|---|---|
| [simulator/config.py](simulator/config.py) | Variables d'env, auth scheme, params spécifiques |
| [simulator/auth.py](simulator/auth.py) | Garder `require_api_key` ou `require_basic_auth`, supprimer l'autre |
| [simulator/generators/base.py](simulator/generators/base.py) | Ajouter les helpers spécifiques à ton API |
| [simulator/generators/example.py](simulator/generators/example.py) | **Renommer** + remplacer les champs par ceux de ton API |
| [simulator/routes/example.py](simulator/routes/example.py) | **Renommer** + URL, méthode HTTP, paramètres |
| [simulator/app.py](simulator/app.py) | Nom du service, import des blueprints |
| [cloudbuild.yaml](cloudbuild.yaml) | Remplacer `MY_SERVICE` |
| [deploy-cloudrun.sh](deploy-cloudrun.sh) | `SERVICE_NAME`, `REPO_NAME`, env vars |
| [deployment/app.yaml](deployment/app.yaml) | Variables d'environnement |

Cherche tous les `# TODO:` dans le code pour ne rien oublier :
```bash
grep -r "TODO" simulator/ deployment/ *.yaml *.sh
```

### 3. Tester en local

```bash
cd simulator
pip install -r requirements.txt
python app.py
# → http://localhost:8080
```

```bash
curl http://localhost:8080/health
curl -H "x-api-key: change-me" http://localhost:8080/api/v1/records
```

### 4. Déployer sur GCP

```bash
bash deploy-cloudrun.sh
```

Voir [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) pour le guide complet.

## Structure du projet

```
simulator/
├── app.py                    # Flask app factory — register blueprints here
├── auth.py                   # Decorators: require_api_key / require_basic_auth
├── config.py                 # Config class (env vars)
├── requirements.txt          # Flask + Faker + xsiam-shared-personas
├── generators/
│   ├── base.py               # Shared helpers + persona imports (do not edit imports)
│   └── example.py            # TODO: rename & replace with your data model
└── routes/
    └── example.py            # TODO: rename & replace with your API endpoints
deployment/
├── Dockerfile                # python:3.11-slim + git + pip install
└── app.yaml                  # App Engine config (optional)
cloudbuild.yaml               # GCP Cloud Build
deploy-cloudrun.sh            # One-command deploy script
```

## Personas partagés — Business Corp

Ces données sont fixes et identiques dans tous les simulateurs. **Ne pas modifier ici**, modifier dans [xsiam-shared-personas](https://github.com/JCourtemanche/xsiam-shared-personas).

| Utilisateur | Email | Hostname | IP | OS |
|---|---|---|---|---|
| Alice Dupont | alice.dupont@business.org | BSNS-WIN-ALICE | 192.168.1.1 | Windows 10 Pro |
| Bob Martin | bob.martin@business.org | BSNS-MAC-BOB | 192.168.1.2 | macOS 13 Ventura |
| Charlie Durant | charlie.durant@business.org | BSNS-WIN-CHARLIE | 192.168.1.3 | Windows 11 Pro |
| David Lefebvre | david.lefebvre@business.org | BSNS-WIN-DAVID | 192.168.1.4 | Windows 10 Pro |
| Emma Leroy | emma.leroy@business.org | BSNS-MAC-EMMA | 192.168.1.5 | macOS 14 Sonoma |
| Flora Moreau | flora.moreau@business.org | BSNS-MOB-FLORA | 192.168.1.6 | iOS 17 |
