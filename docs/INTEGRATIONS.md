# Integration setup guide

Atlas queries enabled integrations for diagnostic evidence. All current
integrations are read-only.

## Docker

Docker is enabled by default. The backend Compose service mounts the Docker
socket and invokes fixed, bounded inventory commands.

```env
ATLAS_DOCKER_ENABLED=true
ATLAS_DOCKER_GID=0
```

On Linux, replace `0` with the group ID of `/var/run/docker.sock`:

```sh
stat -c '%g' /var/run/docker.sock
```

Restart the backend after a change.

## Kubernetes

Atlas reads pods, deployments, recent events, and selected pod logs.

```env
ATLAS_KUBERNETES_ENABLED=true
```

Docker Compose mounts `${KUBECONFIG}` or `~/.kube/config` into the backend.
Verify it from the container:

```powershell
docker compose exec backend kubectl get pods --all-namespaces
```

Use a read-only credential with the least required permissions.

## Prometheus and Grafana

The default Compose stack runs Prometheus and Grafana locally. Atlas reads
Prometheus targets and alerts through:

```env
ATLAS_MONITORING_ENABLED=true
ATLAS_PROMETHEUS_BASE_URL=http://prometheus:9090
```

Prometheus scrapes the backend `/metrics` endpoint. Grafana uses the provisioned
Atlas overview dashboard. Change host ports with the corresponding
`ATLAS_*_PORT` variables.

## Icecast and Liquidsoap

Atlas reads Icecast status JSON and can check an optional Liquidsoap health
endpoint:

```env
ATLAS_RADIO_ENABLED=true
ATLAS_ICECAST_STATUS_URL=http://192.168.2.5:8030/status-json.xsl
ATLAS_LIQUIDSOAP_HEALTH_URL=
```

Test the URL from the Docker host before enabling it. It must be reachable from
the backend container as well.

## Synology

Atlas inventories host-mounted paths; it does not connect to DSM or retain
Synology credentials. For a Windows `Z:\` share root:

```env
ATLAS_SYNOLOGY_ENABLED=true
ATLAS_SYNOLOGY_HOST_PATH=Z:/
ATLAS_SYNOLOGY_MOUNTS=main-share=/mnt/synology,music=/mnt/synology/Music
```

Use the required Compose overlay:

```powershell
docker compose -f docker-compose.yml -f docker-compose.synology.yml up -d --build
```

All paths should be read-only from Docker's perspective.

## GitHub

Atlas lists open pull requests for an explicit allowlist:

```env
ATLAS_GITHUB_ENABLED=true
ATLAS_GITHUB_REPOSITORIES=andrehendriks/animated-invention
ATLAS_GITHUB_TOKEN=
```

Public repositories can omit the token. For private repositories, use a
fine-grained read-only token and recreate the backend after adding it.

## Backup inventory

Atlas can list direct metadata for a mounted backup directory:

```env
ATLAS_BACKUP_ENABLED=true
ATLAS_BACKUP_HOST_PATH=Z:/AtlasBackups
ATLAS_BACKUP_PATH=/mnt/atlas-backups
```

Start it with:

```powershell
docker compose -f docker-compose.yml -f docker-compose.backup.yml up -d --build
```

This integration does not read backup contents or restore data.
