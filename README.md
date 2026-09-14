# Project Atlas

Project Atlas is a local-first HomeLab assistant. This MVP provides a FastAPI
diagnostics API, an Ollama-powered chat endpoint, read-only Docker and
Kubernetes inventory endpoints, local SQLite history, Prometheus/Grafana
observability, and a responsive React dashboard.

## Start locally

1. Copy `.env.example` to `.env` and set the required values.
2. Start the stack with `docker compose up --build`.
3. Open `http://localhost:8080`; the API documentation is at
   `http://localhost:8000/docs`.

Docker diagnostics require access to the Docker socket. Kubernetes diagnostics
require a valid kubeconfig when running with Docker Compose, or the included
read-only `atlas-diagnostics` service account when deployed in Kubernetes. The
API never executes mutating Docker or Kubernetes commands.

Chat and incident history is stored locally in SQLite. Docker Compose retains
it in the named `atlas-data` volume, while Kubernetes uses a 1 GiB
`atlas-data` persistent volume claim; see `docs\DEPLOYMENT.md` for retention
and storage-class guidance.

Set `ATLAS_BACKEND_PORT` or `ATLAS_FRONTEND_PORT` in `.env` when the default
host ports 8000 or 8080 are already in use.

Docker Compose also runs Prometheus locally at `http://localhost:9090` by
default. It scrapes the backend's public `/metrics` endpoint; configure
`ATLAS_PROMETHEUS_PORT` if port 9090 is occupied. Grafana is available at
`http://localhost:3000`; replace its example administrator password before
exposing it outside a trusted LAN.

Run the isolated runtime verification with:

```powershell
.\scripts\smoke-compose.ps1
```

It creates and removes a temporary Compose project, including its own volumes,
and verifies service health, frontend/API proxying, Docker diagnostics,
Prometheus scraping and alert rules, and Grafana dashboard provisioning.

## Development

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm ci
npm run dev
```

See `docs\ARCHITECTURE.md`, `docs\DEPLOYMENT.md`, and
`docs\API_REFERENCE.md` for design, deployment, endpoint, and Kubernetes
runtime prerequisites.
