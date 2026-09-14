# PROJECT ATLAS
## AI HomeLab Assistant

Version: 1.0

Author: Andre Hendriks

---

# VISIE

Project Atlas is een lokale AI HomeLab Assistant die het complete homelab begrijpt, monitort, analyseert en uiteindelijk autonoom kan beheren.

Atlas combineert:

- Ollama
- Kubernetes
- Docker
- Synology
- GitHub
- Monitoring
- Logging
- WebUI

tot één intelligent beheersysteem.

Doel:

Vragen kunnen stellen zoals:

- Waarom werkt mijn radiostream niet?
- Welke container gebruikt de meeste resources?
- Welke pod crasht?
- Welke SMB mount faalt?
- Welke deployment is gisteren gewijzigd?
- Maak een backup van alle YAML bestanden.
- Analyseer mijn logs.
- Welke services zijn offline?

---

# PROJECTDOELEN

Atlas moet:

1. Complete homelab inventaris kennen.
2. Containers kunnen analyseren.
3. Kubernetes begrijpen.
4. Logs analyseren.
5. Fouten detecteren.
6. Root-cause analyses uitvoeren.
7. Adviezen geven.
8. Zelfstandig taken kunnen uitvoeren.
9. Volledig lokaal werken.
10. Self-hosted zijn.

---

# ARCHITECTUUR

User
↓
WebUI
↓
Atlas API
↓
Atlas Core
↓
┌───────────────────────┐
│ Ollama                │
├───────────────────────┤
│ Kubernetes Agent      │
├───────────────────────┤
│ Docker Agent          │
├───────────────────────┤
│ Synology Agent        │
├───────────────────────┤
│ GitHub Agent          │
├───────────────────────┤
│ Monitoring Agent      │
├───────────────────────┤
│ Backup Agent          │
├───────────────────────┤
│ Automation Agent      │
└───────────────────────┘

---

# TECHNOLOGIE STACK

Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

Frontend

- React
- Vite
- TypeScript

AI

- Ollama
- Llama 3
- Qwen
- DeepSeek

Datastore

- PostgreSQL
- SQLite

Monitoring

- Prometheus
- Grafana

Deployment

- Docker
- Kubernetes

---

# REPOSITORY STRUCTUUR

animated-invention

backend/
frontend/
infrastructure/
agents/
prompts/
docs/
scripts/

---

# FASE 1

MVP

Doel:

Werkende AI chatinterface voor het homelab.

Functionaliteit:

✅ Chat

✅ Ollama

✅ Kubernetes read-only

✅ Docker read-only

✅ Logs bekijken

✅ Dashboard

Gebruiker kan vragen:

- Welke pods draaien?
- Welke containers gebruiken geheugen?
- Welke services zijn offline?

---

# FASE 2

KUBERNETES AGENT

Tools:

kubectl get pods

kubectl get deployments

kubectl describe pod

kubectl logs

Voorbeelden:

Waarom crasht liquidsoap?

Welke pods zijn unhealthy?

Geef events van vandaag.

---

# FASE 3

DOCKER AGENT

Tools:

docker ps

docker stats

docker logs

Voorbeelden:

Welke container gebruikt de meeste CPU?

Welke container herstart continu?

Toon container logs.

---

# FASE 4

SYNOLOGY AGENT

Functionaliteit:

Volumes

Shares

SMB

NFS

Storage

Voorbeelden:

Hoeveel ruimte is nog vrij?

Welke NFS exports bestaan?

Is share Dj beschikbaar?

---

# FASE 5

LOG ANALYSIS ENGINE

Bronnen:

Docker

Kubernetes

Icecast

Liquidsoap

Synology

Functionaliteit:

Automatische analyse

Error detectie

Root cause analyse

Voorbeeld:

Vraag:

Waarom werkt mijn stream niet?

Antwoord:

Icecast was offline om 08:42.

Liquidsoap ontving ECONNREFUSED.

Probleem opgelost om 08:51.

---

# FASE 6

GITHUB AGENT

Functionaliteit:

Repositories

Commits

Pull Requests

Actions

Issues

Voorbeelden:

Welke commit veroorzaakte probleem X?

Maak issue aan.

Maak release v1.0.

---

# FASE 7

HOME DASHBOARD

Secties:

Home

Containers

Pods

Storage

GitHub

Monitoring

Radio

AI

Status wordt weergegeven als:

Groen

Oranje

Rood

---

# FASE 8

RADIO MODULE

Integratie:

Icecast

Liquidsoap

WebUI

Functies:

Now Playing

Luisteraars

Bitrate

Historie

DJ informatie

---

# FASE 9

BACKUP ENGINE

Ondersteuning:

YAML

Databases

Config files

Git repositories

Docker volumes

Functies:

Automatische backup

Automatische restore

Backup status

---

# FASE 10

AUTONOME ACTIES

Atlas mag zelfstandig:

Restart deployment

Herstel containers

Opschonen logs

Opschalen replica's

Waarschuwingen versturen

Voorbeeld:

Liquidsoap crasht.

Atlas:

1 analyseert logs
2 vindt oorzaak
3 herstart deployment
4 controleert stream
5 meldt resultaat

---

# FASE 11

KNOWLEDGE GRAPH

Atlas bouwt kennis van:

Synology

Docker

Kubernetes

GitHub

Radio Stack

Muziekbibliotheek

Voorbeeld:

Vraag:

Waarom werkte de stream vorige maand niet?

Atlas zoekt eerdere incidenten.

---

# FASE 12

VOICE INTERFACE

Integratie:

Whisper

Piper TTS

Ollama

Voorbeeld:

"Atlas, waarom gebruikt Ollama zoveel geheugen?"

Atlas antwoordt gesproken.

---

# FASE 13

MULTI AGENT MODE

Agents werken samen.

Voorbeeld:

User:
Waarom werkt Icecast niet?

Workflow:

Log Agent
↓
Kubernetes Agent
↓
Docker Agent
↓
Ollama Analyse

Antwoord:

Volledige root cause analyse.

---

# VEILIGHEID

Verplicht:

Authenticatie

RBAC

