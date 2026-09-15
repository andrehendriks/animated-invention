# Configuration reference

Atlas reads its configuration from the root `.env` file through Docker Compose.
Copy `.env.example` before first use. Keep `.env` local: it can contain
passwords and API keys.

```powershell
Copy-Item .env.example .env
```

After changing a backend setting, recreate `backend`. After changing
`ATLAS_NGINX_PROXY_TIMEOUT_SECONDS`, recreate `frontend`.

```powershell
docker compose up -d --force-recreate backend frontend
```

## Core and access

| Variable | Default | Purpose |
| --- | --- | --- |
| `ATLAS_APP_NAME` | `Project Atlas` | Application name. |
| `ATLAS_ENVIRONMENT` | `development` | Environment label. |
| `ATLAS_AUTH_ENABLED` | `false` | Require an API key for non-probe API routes. |
| `ATLAS_API_KEY` | empty | API key sent as `X-API-Key` when authentication is enabled. |
| `ATLAS_ALLOWED_ORIGINS` | local Vite and dashboard origins | Comma-separated exact browser origins permitted by the API. |
| `ATLAS_DATABASE_PATH` | `/data/atlas.db` | SQLite path in the backend container. |
| `ATLAS_HISTORY_MAX_ENTRIES` | `1000` | Maximum retained local chat and incident records. |

Use a long, unique API key before exposing Atlas beyond a trusted network:

```env
ATLAS_AUTH_ENABLED=true
ATLAS_API_KEY=replace-with-a-long-unique-secret
ATLAS_ALLOWED_ORIGINS=http://atlas-host:38101
```

## Network ports

All values are host ports. They may be changed when a port is occupied.

| Variable | Default | Container port | Service |
| --- | ---: | ---: | --- |
| `ATLAS_BACKEND_PORT` | `8000` | `8000` | Atlas API |
| `ATLAS_FRONTEND_PORT` | `8080` | `8080` | Atlas dashboard |
| `ATLAS_PROMETHEUS_PORT` | `9090` | `9090` | Prometheus |
| `ATLAS_GRAFANA_PORT` | `3000` | `3000` | Grafana |

For example:

```env
ATLAS_BACKEND_PORT=38100
ATLAS_FRONTEND_PORT=38101
ATLAS_PROMETHEUS_PORT=38102
ATLAS_GRAFANA_PORT=38103
```

## Ollama and chat

| Variable | Default | Purpose |
| --- | --- | --- |
| `ATLAS_OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama endpoint reachable from the backend. |
| `ATLAS_OLLAMA_MODEL` | `llama3.2` | Model sent to Ollama for chat. |
| `ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS` | `180` | Backend wait time for one non-streaming chat response. |
| `ATLAS_NGINX_PROXY_TIMEOUT_SECONDS` | `630` | Frontend proxy timeout; keep above the Ollama request timeout. |

For a slower CPU-only host:

```env
ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS=600
ATLAS_NGINX_PROXY_TIMEOUT_SECONDS=630
```

Pull the configured model after the stack starts:

```powershell
docker compose exec ollama ollama pull llama3.2
```

## Diagnostics integrations

| Variable | Default | Purpose |
| --- | --- | --- |
| `ATLAS_DOCKER_ENABLED` | `true` | Enable read-only Docker inventory, stats, and logs. |
| `ATLAS_DOCKER_GID` | `0` | Docker socket group ID for the non-root backend user. |
| `ATLAS_KUBERNETES_ENABLED` | `true` | Enable read-only Kubernetes diagnostics. |
| `ATLAS_SYNOLOGY_ENABLED` | `false` | Enable configured storage-mount inventory. |
| `ATLAS_SYNOLOGY_MOUNTS` | empty | Comma-separated `name=/container/path` mount mappings. |
| `ATLAS_MONITORING_ENABLED` | `true` | Enable Prometheus alerts and target diagnostics. |
| `ATLAS_PROMETHEUS_BASE_URL` | `http://prometheus:9090` | Prometheus endpoint available to the backend. |
| `ATLAS_GITHUB_ENABLED` | `false` | Enable read-only open-pull-request inventory. |
| `ATLAS_GITHUB_REPOSITORIES` | empty | Comma-separated `owner/repository` values. |
| `ATLAS_GITHUB_TOKEN` | empty | Optional read-only GitHub token; required for private repositories. |

Docker access is powerful even when Atlas issues only read commands. Enable it
only on trusted hosts. On Linux, set `ATLAS_DOCKER_GID` to the numeric group of
the mounted Docker socket.

## Radio, storage, and backup

| Variable | Default | Purpose |
| --- | --- | --- |
| `ATLAS_RADIO_ENABLED` | `false` | Enable Icecast/Liquidsoap diagnostics. |
| `ATLAS_ICECAST_STATUS_URL` | `http://icecast:8000/status-json.xsl` | Read-only Icecast JSON status URL. |
| `ATLAS_LIQUIDSOAP_HEALTH_URL` | empty | Optional read-only Liquidsoap health URL. |
| `ATLAS_BACKUP_ENABLED` | `false` | Enable read-only backup-directory inventory. |
| `ATLAS_BACKUP_PATH` | `/mnt/atlas-backups` | Backup path inside the backend container. |

`ATLAS_SYNOLOGY_HOST_PATH` and `ATLAS_BACKUP_HOST_PATH` are Compose-overlay
variables. They define host paths and are required only when the related
overlay is used:

```env
ATLAS_SYNOLOGY_HOST_PATH=Z:/
ATLAS_SYNOLOGY_MOUNTS=main-share=/mnt/synology
ATLAS_BACKUP_HOST_PATH=Z:/AtlasBackups
```

Start the corresponding overlay with the base Compose file:

```powershell
docker compose -f docker-compose.yml -f docker-compose.synology.yml up -d
docker compose -f docker-compose.yml -f docker-compose.backup.yml up -d
```

## Grafana

| Variable | Default | Purpose |
| --- | --- | --- |
| `ATLAS_GRAFANA_ADMIN_USER` | `atlas` | Grafana administrator user. |
| `ATLAS_GRAFANA_ADMIN_PASSWORD` | example value | Grafana administrator password. |

Replace the password before any network exposure. Recreate Grafana after
changing its credentials.
