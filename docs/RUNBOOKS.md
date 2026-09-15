# Operational runbooks

Use these runbooks to investigate Atlas safely. Atlas integrations are
read-only; proposed automation plans do not execute changes.

## First response

Collect the current state before restarting anything:

```powershell
docker compose ps
docker compose logs --tail 100 backend frontend ollama
```

Record the error, time, affected service, and any recent configuration change.

## Chat returns 504

1. Verify Ollama has the configured model:

   ```powershell
   docker compose exec ollama ollama list
   ```

2. Check active timeout settings:

   ```powershell
   docker compose exec backend python -c "from app.config import get_settings; print(get_settings().ollama_request_timeout_seconds)"
   docker compose exec frontend nginx -T 2>&1 | Select-String "proxy_.*timeout"
   ```

3. For a slow host, configure a backend timeout and a larger proxy timeout:

   ```env
   ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS=600
   ATLAS_NGINX_PROXY_TIMEOUT_SECONDS=630
   ```

4. Rebuild and recreate backend and frontend:

   ```powershell
   docker compose up -d --build --force-recreate backend frontend
   ```

If the problem continues, collect the logs immediately after reproducing it.

## Chat returns 503

`503` normally means the backend cannot reach Ollama.

```powershell
docker compose ps ollama backend
docker compose logs --tail 100 ollama backend
docker compose exec ollama ollama list
```

If Ollama is healthy but the required model is absent, pull it and retry:

```powershell
docker compose exec ollama ollama pull llama3.2
```

## Host port is already allocated

Find the owner before changing anything:

```powershell
docker ps --format "table {{.Names}}`t{{.Ports}}"
Get-NetTCPConnection -LocalPort 8080 | Select-Object LocalAddress, LocalPort, OwningProcess
```

Either stop the known obsolete service or choose a free host port in `.env`,
then recreate the affected service:

```env
ATLAS_FRONTEND_PORT=38101
```

```powershell
docker compose up -d --force-recreate frontend
```

## Icecast is unavailable

Test the exact public status endpoint from the Docker host:

```powershell
Invoke-WebRequest http://192.168.2.5:8030/status-json.xsl -UseBasicParsing
```

Confirm `ATLAS_RADIO_ENABLED=true` and the URL in `.env`, then recreate the
backend:

```powershell
docker compose up -d --force-recreate backend
```

The endpoint must return JSON with an `icestats` object.

## Synology path does not exist

The backend sees container paths only. Confirm the host path is accessible to
Docker and start Atlas with the storage overlay:

```env
ATLAS_SYNOLOGY_ENABLED=true
ATLAS_SYNOLOGY_HOST_PATH=Z:/
ATLAS_SYNOLOGY_MOUNTS=main-share=/mnt/synology
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.synology.yml up -d --force-recreate backend
```

Do not use a plain `docker compose up` later for this deployment: it removes
the additional bind mount when the backend is recreated.

## Docker diagnostics fail

Confirm the socket mount and backend logs:

```powershell
docker compose exec backend ls -l /var/run/docker.sock
docker compose logs --tail 100 backend
```

On Linux, use the numeric socket group for `ATLAS_DOCKER_GID`. On Docker
Desktop, the default value of `0` is normally appropriate.

## Kubernetes diagnostics fail

Check that Kubernetes is enabled and a valid kubeconfig is mounted:

```powershell
docker compose exec backend kubectl config current-context
docker compose exec backend kubectl get pods --all-namespaces
```

Use a least-privilege kubeconfig. Atlas needs only read permissions for the
supported diagnostic resources.

If the host command works but the backend reports a refused connection to
`127.0.0.1:<port>`, generate a Docker Desktop container kubeconfig:

```powershell
.\scripts\create-docker-desktop-kubeconfig.ps1
```

Set the generated `.atlas\kubeconfig` path as `ATLAS_KUBECONFIG_PATH` in
`.env`, then recreate the backend.

## Smoketest fails

The smoketest uses temporary host ports. If a port is occupied, select other
free ports:

```powershell
.\scripts\smoke-compose.ps1 `
  -BackendPort 48000 `
  -FrontendPort 48001 `
  -PrometheusPort 49090 `
  -GrafanaPort 43000
```

Successful output ends with `Compose smoke test passed.` The temporary
containers, volumes, and network are removed automatically.
