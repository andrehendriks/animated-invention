# Deployment

## Docker Compose

Copy the root `.env.example` to `.env`, choose an Ollama model, and run:

```sh
docker compose up --build
```

Set `ATLAS_BACKEND_PORT` and `ATLAS_FRONTEND_PORT` in `.env` to choose
different host ports when 8000 or 8080 are occupied.

Prometheus starts with the stack and stores its time series in the
`prometheus-data` volume. Its configuration scrapes the backend's public
`/metrics` endpoint every 15 seconds. Change `ATLAS_PROMETHEUS_PORT` when the
default host port 9090 is occupied. It raises `AtlasBackendDown` after two
minutes of failed scrapes and `AtlasBackendHighMemory` after ten minutes above
384 MiB resident memory; inspect these through Atlas or Grafana. Atlas does
not run Alertmanager or send external notifications by default, so alerts stay
within the local deployment.

Grafana starts at `http://localhost:3000` with Prometheus preconfigured as its
default datasource. Set `ATLAS_GRAFANA_ADMIN_PASSWORD` to a unique value before
exposing it beyond a trusted LAN, and change `ATLAS_GRAFANA_PORT` when port
3000 is occupied. The provisioned **Atlas overview** dashboard shows backend
availability, CPU usage, and resident memory.

Pull the selected model after Ollama has started, for example:

```sh
docker compose exec ollama ollama pull llama3.2
```

Compose waits for Ollama before starting the backend, and waits for the
backend's `/api/ready` check before starting the frontend.
Atlas waits up to 180 seconds for a non-streaming Ollama chat response by
default. Set `ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS` in `.env` for a slower
model or host, then set `ATLAS_NGINX_PROXY_TIMEOUT_SECONDS` above that value.
The Nginx proxy default is 630 seconds.

Run the isolated Compose smoketest to rebuild the stack, wait for all services,
verify the frontend, its `/api/health` proxy, its read-only Docker inventory
route, the `atlas-backend` Prometheus scrape target, and both local Atlas
alert rules, then remove the temporary containers and network. It also
authenticates against Grafana using the configured administrator credentials
and verifies the provisioned `atlas-overview` dashboard:

```powershell
.\scripts\smoke-compose.ps1
```

It uses high, configurable ports by default to avoid a local Atlas instance or
other applications: `-FrontendPort 18081 -BackendPort 18001`. The selected
ports must be free for the duration of the test. Each run uses a separate
Compose project and temporary volumes, which are deleted on completion; it
does not reuse or remove the persistent data of a local Atlas deployment.
Use `.\scripts\smoke-compose.ps1 -Authentication` to run the same validation
with temporary API-key authentication enabled; it verifies that the protected
Docker route rejects requests without the key and succeeds with it.

The backend has read-only access to the Docker socket and kubeconfig solely for
diagnostics. Do not enable those mounts on an untrusted host. Set
`ATLAS_AUTH_ENABLED=true` and a unique `ATLAS_API_KEY` before exposing Atlas
beyond a trusted LAN.

The backend image includes only the Docker and Kubernetes **client** binaries.
Docker Desktop exposes the socket as group `0`, which is the default
`ATLAS_DOCKER_GID`. On Linux, replace it with the numeric group of
`/var/run/docker.sock` (for example, `stat -c '%g' /var/run/docker.sock`) so
the non-root `atlas` user can use the mounted socket. Keep Docker diagnostics
disabled if that socket access is not explicitly required.

## Local history

Chat requests and incident reports are stored locally in SQLite at
`ATLAS_DATABASE_PATH` (default: `/data/atlas.db`). Docker Compose persists this
directory in the `atlas-data` volume. The history includes the submitted prompt
and the returned response or incident report, so do not store sensitive values
in Atlas prompts. Atlas retains the latest 1,000 records by default; adjust
`ATLAS_HISTORY_MAX_ENTRIES` only when additional local retention is required.
Use the dashboard's **Clear local history** action, or authenticated
`DELETE /api/history`, to permanently remove all local history records.
Kubernetes persists the same directory with the 1 GiB,
`ReadWriteOnce` `atlas-data` PVC. It uses the cluster's default storage class;
add `storageClassName` or change the requested capacity in `data-pvc.yaml`
before applying it when the cluster requires a specific provisioner.

## Synology storage

Atlas reads mounted Synology shares; it does not store DSM credentials or issue
NAS commands. Mount each share read-only on the Docker host, bind-mount it
read-only into `backend` with the optional overlay, set
`ATLAS_SYNOLOGY_ENABLED=true`, and populate
`ATLAS_SYNOLOGY_MOUNTS` with logical names and container paths, for example
`media=/mnt/synology/media`. Only those configured paths are inspected.

```sh
ATLAS_SYNOLOGY_HOST_PATH=/srv/synology \
  docker compose -f docker-compose.yml -f docker-compose.synology.yml up --build
```

## Monitoring

Set `ATLAS_MONITORING_ENABLED=true` and point `ATLAS_PROMETHEUS_BASE_URL` at a
trusted local Prometheus server. Atlas performs only `GET` requests to
Prometheus's alert and target APIs; it does not create, silence, or resolve
alerts.

## GitHub

Set `ATLAS_GITHUB_ENABLED=true` and list the repositories Atlas may inspect in
`ATLAS_GITHUB_REPOSITORIES`. `ATLAS_GITHUB_TOKEN` is optional for public
repositories; for private repositories, use a fine-grained token limited to
read-only Pull requests and Metadata access. Atlas only lists open pull
requests and never creates or changes GitHub resources.

## Radio

Set `ATLAS_RADIO_ENABLED=true` and configure
`ATLAS_ICECAST_STATUS_URL` to Icecast's public `status-json.xsl` endpoint.
`ATLAS_LIQUIDSOAP_HEALTH_URL` is optional and must be a read-only health
endpoint. Atlas reads stream metadata and listener counts only; it does not
modify Icecast, Liquidsoap, playlists, or mounts.

## Backup inventory

Set `ATLAS_BACKUP_ENABLED=true` and mount the backup directory read-only with
the optional overlay. Atlas lists only direct file metadata; it never creates,
reads, modifies, uploads, restores, or deletes backup files.

```sh
ATLAS_BACKUP_HOST_PATH=/srv/atlas-backups \
  docker compose -f docker-compose.yml -f docker-compose.backup.yml up --build
```

## Security posture

`GET /api/security/posture` performs a local configuration assessment. It never
scans hosts, networks, files, containers, or credentials, and never returns
secret values. Enable API-key authentication and use exact CORS origins before
exposing Atlas outside a trusted LAN.

## Automation

`POST /api/automation/plans` creates deterministic **observe-only** remediation
plans. It does not run commands or change Docker, Kubernetes, storage, radio,
backup, or GitHub resources. Any future action executor should require
per-action authorization and independently revalidate the collected evidence.

## Log analysis

`POST /api/logs/analyze` processes only the raw logs included in that request.
It groups common error signatures and extracts timestamps in memory; it does
not persist, forward, modify, or retrieve logs from any system.

## Incident analysis

`POST /api/incidents/analyze` selects diagnostic agents based on the reported
symptoms and produces a structured incident report. Atlas reports the root
cause as undetermined until collected evidence establishes causality; it does
not speculate or execute remediation.

## Kubernetes diagnostics

Atlas uses only `kubectl get pods --all-namespaces -o json`,
`kubectl get deployments --all-namespaces -o json`, and the latest 100 cluster
events. It can also read explicitly selected pod logs with `kubectl logs`,
validating namespace and pod names and limiting responses to 1,000 lines and
100 KB. Bind a kubeconfig or use a dedicated Kubernetes service account with
least-privilege `get` and `list` permissions, including `get` on the
`pods/log` subresource; no Kubernetes mutation permission is required.

## Docker diagnostics

Atlas uses `docker ps` and `docker stats --no-stream` only. It requires Docker
socket access to collect this inventory, so enable it only on trusted hosts and
do not grant Atlas write access to Docker management APIs.

Container logs are read with `docker logs --tail`, validating the container
name or ID and limiting the request to 1,000 lines and 100 KB of returned text.

## Kubernetes

Create a real secret from `secrets.example.yaml` without committing it, then
apply the deployable manifest bundle. The example secret is intentionally not
part of the bundle.

```sh
kubectl apply -k infrastructure/kubernetes
```

For Docker Desktop Kubernetes, build the local images, tag them with the
manifest names, create a local-only secret, then apply the Docker Desktop
overlay. It uses `IfNotPresent` only for the locally built backend, frontend
and Grafana images; the base manifests remain suitable for a registry-backed
deployment.

```powershell
docker build --tag project-atlas/backend:latest .\backend
docker build --tag project-atlas/frontend:latest .\frontend
docker build --tag project-atlas/grafana:latest .\infrastructure\grafana
kubectl create namespace atlas
kubectl create secret generic atlas-secrets --namespace atlas `
  --from-literal=ATLAS_AUTH_ENABLED=true `
  --from-literal=ATLAS_API_KEY=<unique-api-key> `
  --from-literal=ATLAS_DOCKER_ENABLED=false `
  --from-literal=ATLAS_OLLAMA_BASE_URL=http://ollama.atlas.svc.cluster.local:11434 `
  --from-literal=ATLAS_MONITORING_ENABLED=true `
  --from-literal=ATLAS_PROMETHEUS_BASE_URL=http://prometheus.atlas.svc.cluster.local:9090 `
  --from-literal=GF_SECURITY_ADMIN_USER=atlas `
  --from-literal=GF_SECURITY_ADMIN_PASSWORD=<unique-grafana-password> `
  --from-literal=GF_USERS_ALLOW_SIGN_UP=false
kubectl apply -k infrastructure/docker-desktop-kubernetes
```

The Docker Desktop overlay sets the frontend `LoadBalancer` service to port
8081, avoiding a conflict with an occupied host port 80. Some Docker Desktop
installations do not route LoadBalancer or NodePort services to Windows. In
that case, use the reliable local access method:

```powershell
kubectl port-forward --namespace atlas service/atlas-frontend 8081:8081
```

Then open `http://localhost:8081`. To make this local frontend access
persistent for the current Windows user, the scheduled task uses
`http://localhost:18081` to avoid a stale Docker Desktop binding on port 8081.
The base service remains a port-80
`LoadBalancer` for registry-backed cluster deployments.

To make this local frontend access persistent for the current Windows user,
install the scheduled port-forward task once:

```powershell
.\scripts\install-atlas-frontend-port-forward-task.ps1
```

The task starts at user logon, retries up to 999 times after an unexpected
failure, and writes output to
`%LOCALAPPDATA%\ProjectAtlas\logs\frontend-port-forward.log`. It copies its
small start script to `%LOCALAPPDATA%\ProjectAtlas\scripts` so it remains
available even if the project drive is not mounted at logon. It refuses to
take over an occupied local port 18081. Remove it with:

```powershell
.\scripts\uninstall-atlas-frontend-port-forward-task.ps1
```

`ollama.yaml` persists models in a 20 GiB `ReadWriteOnce` PVC and requests 1
CPU/4 GiB memory, with limits of 4 CPU/8 GiB. Change these values and add a
specific `storageClassName` before applying when necessary. The frontend uses a
`LoadBalancer` service; change its type to match the cluster's ingress or
networking setup. The base manifests use published GHCR images from
`ghcr.io/andrehendriks/animated-invention`. CI publishes `latest` and
commit-SHA tags after each push to `main`; prefer a tested SHA tag for a
production deployment. If the GHCR packages are private, create an
`imagePullSecret` and add it to the workload pod specs before deployment.

`prometheus.yaml` keeps time series in a 10 GiB `ReadWriteOnce` PVC and
scrapes `backend:8000/metrics` every 15 seconds. It requests 100m CPU and
256Mi memory, with 500m CPU and 1Gi memory limits. Adjust storage and resource
values for the cluster before applying it.

`grafana.yaml` uses a 2 GiB `ReadWriteOnce` PVC and a `LoadBalancer` service.
CI publishes its image from `infrastructure/grafana` alongside backend and
frontend images; set a unique `GF_SECURITY_ADMIN_PASSWORD` in the Kubernetes
secret before deploying.

The Kubernetes secret example enables API-key authentication. Before deploying,
replace `ATLAS_API_KEY` with a unique secret, then enter that key in the
dashboard's **API key** field. The key is retained only in the browser session
and sent in the `X-API-Key` header; closing the browser tab clears it.

The backend runs as the dedicated `atlas-diagnostics` service account. Its
cluster-wide access is limited to reading pods, deployments, events, and the
`pods/log` subresource; it has no mutation permissions. The deployment
manifest also defaults to a restricted container security context, requests
100m CPU and 256Mi memory, and is limited to 500m CPU and 512Mi memory.
Kubernetes uses `/api/health` for liveness and `/api/ready` for readiness, so
the pod becomes ready only after Ollama is reachable.
