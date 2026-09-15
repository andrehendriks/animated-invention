# Atlas user and administrator guide

This guide covers the day-to-day operation of a Docker Compose deployment of
Project Atlas. Atlas is local-first: its history remains in local storage, and
the integrations collect read-only diagnostic data.

## Before you start

Atlas requires Docker Desktop or Docker Engine with Docker Compose v2. The
backend's Docker diagnostics also require access to the Docker socket.

Create the local configuration once:

```powershell
Copy-Item .env.example .env
```

Edit `.env` before exposing Atlas to other devices. Do not commit `.env`: it
can contain API keys and passwords.

## Starting Atlas

For a standard installation:

```powershell
docker compose up -d --build
docker compose ps
```

The `ps` output should show `healthy` for `ollama`, `backend`, `frontend`, and
`grafana`. Prometheus has no container healthcheck, so `Up` is expected.

Use the host ports configured in `.env`:

| Service | Environment variable | Default URL |
| --- | --- | --- |
| Atlas dashboard | `ATLAS_FRONTEND_PORT` | `http://localhost:8080` |
| Atlas API and OpenAPI | `ATLAS_BACKEND_PORT` | `http://localhost:8000/docs` |
| Prometheus | `ATLAS_PROMETHEUS_PORT` | `http://localhost:9090` |
| Grafana | `ATLAS_GRAFANA_PORT` | `http://localhost:3000` |

For example, if `.env` sets `ATLAS_FRONTEND_PORT=38101`, open
`http://localhost:38101` on the host. From another LAN device, replace
`localhost` with the server's IP address or hostname.

## Preparing chat

Atlas requires an Ollama model for chat. Pull the model configured by
`ATLAS_OLLAMA_MODEL`; the default is `llama3.2`:

```powershell
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama list
```

The first answer can take longer while Ollama loads the model. Atlas waits
`ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS` (default: 180 seconds). When a slower
host needs more time, increase this setting and keep
`ATLAS_NGINX_PROXY_TIMEOUT_SECONDS` higher than it:

```env
ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS=600
ATLAS_NGINX_PROXY_TIMEOUT_SECONDS=630
```

Apply changed environment values by recreating the affected services:

```powershell
docker compose up -d --force-recreate backend frontend
```

In the dashboard, enter a question in **Ask Atlas** and press **Enter** or
select **Send**. Atlas returns evidence it collected along with its response.

## Radio diagnostics

Enable the radio integration and use an Icecast status endpoint reachable from
the backend container:

```env
ATLAS_RADIO_ENABLED=true
ATLAS_ICECAST_STATUS_URL=http://192.168.2.5:8030/status-json.xsl
```

After updating `.env`, recreate the backend:

```powershell
docker compose up -d --force-recreate backend
```

The Radio view reports mountpoints, listener counts, and now-playing metadata.
The integration is read-only.

## Synology storage diagnostics

`ATLAS_SYNOLOGY_MOUNTS` names paths **inside the backend container**. The host
directory must also be bind-mounted with the Synology Compose overlay.

For a Windows host where `Z:\` is the mounted share root:

```env
ATLAS_SYNOLOGY_ENABLED=true
ATLAS_SYNOLOGY_HOST_PATH=Z:/
ATLAS_SYNOLOGY_MOUNTS=main-share=/mnt/synology
```

Start or update Atlas with both Compose files whenever Synology diagnostics are
enabled:

```powershell
docker compose -f docker-compose.yml -f docker-compose.synology.yml up -d --build
```

If the host root contains a subdirectory named `Music`, map it separately with
`music=/mnt/synology/Music`. A `No such file or directory` response means the
host path is absent, inaccessible to Docker, or the Synology overlay was not
included.

## Docker Desktop Kubernetes diagnostics

When the Docker-host kubeconfig uses a loopback API address such as
`https://127.0.0.1:57422`, generate the backend-specific configuration:

```powershell
.\scripts\create-docker-desktop-kubeconfig.ps1
```

Set the generated path in `.env` and recreate the backend:

```env
ATLAS_KUBECONFIG_PATH=C:/path/to/animated-invention/.atlas/kubeconfig
```

```powershell
docker compose up -d --force-recreate backend
```

This changes the API address only for the Atlas container; the host's
`kubectl` configuration remains unchanged.

## Routine administration

View service status and recent logs:

```powershell
docker compose ps
docker compose logs --tail 100 backend frontend
```

Restart one service after a configuration or image change:

```powershell
docker compose up -d --force-recreate backend
```

Stop the standard stack without removing its data:

```powershell
docker compose down
```

To stop a Synology-enabled deployment, include the same overlay used to start
it:

```powershell
docker compose -f docker-compose.yml -f docker-compose.synology.yml down
```

Named volumes preserve Ollama models, Atlas history, Prometheus data, and
Grafana data. Do not add `--volumes` to routine shutdowns unless those data are
intentionally being deleted.

## Updating from GitHub

When this checkout uses a `github` remote, fetch the desired branch and merge
the exact fetched commit:

```powershell
git fetch github main
git merge --ff-only FETCH_HEAD
docker compose up -d --build
```

If Git reports local modifications that overlap an update, preserve them before
merging:

```powershell
git stash push --include-untracked -m "Local Atlas changes before update"
git merge --ff-only FETCH_HEAD
git stash pop
```

Resolve any conflict reported by `git stash pop` before rebuilding containers.

## Verifying a deployment

Run the isolated Compose smoketest:

```powershell
.\scripts\smoke-compose.ps1
```

It creates a temporary project, validates all services, frontend/API proxying,
Docker inventory, Prometheus targets and rules, and Grafana provisioning, then
removes the temporary resources. If its default test ports collide with a
running local service, choose free ports:

```powershell
.\scripts\smoke-compose.ps1 `
  -BackendPort 48000 `
  -FrontendPort 48001 `
  -PrometheusPort 49090 `
  -GrafanaPort 43000
```

Successful output ends with `Compose smoke test passed.`

## Security checklist

Before LAN or internet exposure:

1. Replace `ATLAS_GRAFANA_ADMIN_PASSWORD` with a unique password.
2. Set `ATLAS_AUTH_ENABLED=true`.
3. Set a unique `ATLAS_API_KEY` and enter it in the dashboard's **API key**
   field for the current browser session.
4. Set `ATLAS_ALLOWED_ORIGINS` to the exact dashboard origins in use.
5. Enable Docker socket and host-mounted storage access only on trusted hosts.

Atlas has read-only integrations by design. The automation endpoint creates
proposals only; it does not execute infrastructure changes.

## Troubleshooting

| Symptom | Likely cause and action |
| --- | --- |
| `Bind ... port is already allocated` | Choose a free host port in `.env`, then run `docker compose up -d`. |
| Chat returns `504` | Confirm the Ollama model is installed, then increase the two timeout settings together and recreate `backend` and `frontend`. |
| Chat returns `503` | Check `docker compose logs --tail 100 backend ollama` and verify `docker compose exec ollama ollama list`. |
| Icecast is unavailable | Verify the configured status URL from the Docker host and recreate `backend` after changing `.env`. |
| Synology path does not exist | Verify `ATLAS_SYNOLOGY_HOST_PATH` and start using `docker-compose.synology.yml`. |
| A diagnostic integration is disabled | Set its `ATLAS_*_ENABLED` value to `true`, configure its dependency, and recreate `backend`. |

For endpoint details, see [API_REFERENCE.md](API_REFERENCE.md). For deployment
and Kubernetes-specific configuration, see [DEPLOYMENT.md](DEPLOYMENT.md).
