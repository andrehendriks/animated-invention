# Security guide

Atlas is intended for trusted HomeLab environments. It is local-first and its
integrations are read-only, but Docker-socket access, mounted storage, and
operational metadata are sensitive.

## Baseline before network exposure

Set unique credentials in `.env`:

```env
ATLAS_AUTH_ENABLED=true
ATLAS_API_KEY=replace-with-a-long-unique-secret
ATLAS_GRAFANA_ADMIN_USER=atlas
ATLAS_GRAFANA_ADMIN_PASSWORD=replace-with-a-unique-password
ATLAS_ALLOWED_ORIGINS=http://atlas-host:38101
```

Recreate the affected services:

```powershell
docker compose up -d --force-recreate backend grafana
```

The frontend retains an API key only in the active browser tab's
`sessionStorage`. Enter it through the dashboard's **API key** field after
opening the page.

## Exposure guidance

- Prefer access through a trusted LAN, VPN, or reverse proxy with TLS.
- Do not expose the API, Prometheus, or Grafana ports directly to the public
  internet.
- Restrict host firewalls to required source networks.
- Use exact origins in `ATLAS_ALLOWED_ORIGINS`; do not use broad wildcards.
- Keep Docker Desktop, Docker Engine, and container base images current.

## Sensitive integrations

### Docker socket

The backend mounts `/var/run/docker.sock` to read container inventory, one-shot
statistics, and bounded logs. A Docker socket can enable powerful host control
if a service is compromised. Disable Docker diagnostics when not needed:

```env
ATLAS_DOCKER_ENABLED=false
```

Use it only on trusted hosts and do not add write-capable automation.

### Kubernetes

Use a dedicated kubeconfig or service account restricted to the reads Atlas
supports: pods, deployments, events, and selected pod logs. Do not grant
create, update, patch, delete, exec, or cluster-admin permissions.

### Synology and backups

Mount shares and backup directories read-only. Configure only paths Atlas must
inventory. Atlas does not need DSM credentials, SMB passwords, or write
mounts.

### GitHub

For private repositories, use a fine-grained token limited to read-only
Metadata and Pull requests access. Store it only in `.env`; never commit it or
place it in a prompt, chat record, issue, or log.

## Data handling

Atlas stores chat messages, responses, and incident reports in local SQLite
history. Avoid entering credentials, private keys, or sensitive production
data into chat. Clear this history from the dashboard or with:

```powershell
curl.exe -X DELETE http://localhost:8000/api/history -H "X-API-Key: <key>"
```

When authentication is disabled, omit the header. Deletion is permanent.

## Maintenance checklist

1. Rotate the Atlas API key and Grafana password periodically.
2. Review enabled integrations and disable unused ones.
3. Update images and run the smoketest after updates.
4. Back up the Atlas data volume before destructive maintenance.
5. Review Docker, backend, and frontend logs after a suspected incident.

Atlas automation endpoints return proposed plans only. Do not interpret a plan
as a performed action.
