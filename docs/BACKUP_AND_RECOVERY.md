# Backup and recovery guide

Atlas uses Docker named volumes for persistent runtime data:

| Volume | Contains |
| --- | --- |
| `atlas-data` | Local SQLite chat and incident history. |
| `ollama-data` | Downloaded Ollama models. |
| `prometheus-data` | Prometheus time-series data. |
| `grafana-data` | Grafana users, preferences, and runtime state. |

Routine `docker compose down` preserves these volumes. Do not use
`docker compose down --volumes` unless the data is intentionally discarded.

## Backup scope

Back up the repository configuration separately from the volumes:

- Git-tracked files can be restored from GitHub.
- `.env` is intentionally ignored by Git and must be backed up securely.
- Named volumes contain the mutable Atlas, Ollama, Prometheus, and Grafana
  state.

Keep backups encrypted and restrict access because history can contain
operational context and `.env` can contain secrets.

## Backing up a named volume

Stop the service that writes the volume when consistency matters. This example
archives Atlas history to `D:\AtlasBackups`:

```powershell
New-Item -ItemType Directory -Force D:\AtlasBackups
docker compose stop backend
docker run --rm `
  -v animated-invention_atlas-data:/source:ro `
  -v D:\AtlasBackups:/backup `
  alpine tar czf /backup/atlas-data.tgz -C /source .
docker compose start backend
```

Use `docker volume ls` to confirm the actual volume prefix. Compose derives it
from the project name, so another checkout may use a different prefix.

Repeat with the relevant volume name to archive Ollama, Prometheus, or Grafana
state. Backing up Ollama models can be large; consider re-pulling models
instead when bandwidth is acceptable.

## Restoring a named volume

Restoring replaces the current volume contents. Stop the dependent service,
inspect the archive, and retain a copy of current data first.

```powershell
docker compose stop backend
docker run --rm `
  -v animated-invention_atlas-data:/target `
  -v D:\AtlasBackups:/backup:ro `
  alpine sh -c "rm -rf /target/* && tar xzf /backup/atlas-data.tgz -C /target"
docker compose start backend
```

Replace the source and target names for other volumes. Do not restore an
untrusted archive.

## Recovering the application

1. Restore or clone the repository.
2. Restore a securely backed-up `.env`, or copy `.env.example` and re-enter
   configuration and secrets.
3. Start Atlas with the same overlays required by the deployment.
4. Restore named volumes if history, models, or dashboards are required.
5. Run `.\scripts\smoke-compose.ps1` to validate the rebuilt stack.

## Recovery checks

```powershell
docker compose ps
docker compose exec ollama ollama list
docker compose logs --tail 100 backend frontend
```

Open the dashboard and verify the expected history, model availability, and
Grafana configuration. If restoring external storage integrations, confirm
their host paths exist before starting the related overlay.
