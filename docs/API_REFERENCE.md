# API reference

Atlas exposes its API under `/api`. Interactive OpenAPI documentation is
available at `/docs` on the backend port.

When `ATLAS_AUTH_ENABLED=true`, all endpoints except the public probe routes
`GET /api/health` and `GET /api/ready` require the `X-API-Key` header. The
dashboard can store the key for its current browser tab through the **API key**
field. Integration endpoints return `503` when disabled or when their
configured dependency is unavailable.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Atlas and integration configuration status |
| `GET` | `/ready` | Readiness check; confirms that Ollama is reachable |
| `POST` | `/chat` | Evidence-aware Ollama chat; body: `{"message":"..."}` |
| `GET` | `/docker/containers` | Docker container inventory |
| `GET` | `/docker/stats` | One-shot Docker resource statistics |
| `GET` | `/docker/containers/{container}/logs?tail=200` | Bounded container logs |
| `GET` | `/kubernetes/pods` | Cluster-wide pod inventory |
| `GET` | `/kubernetes/deployments` | Cluster-wide deployment replica status |
| `GET` | `/kubernetes/events` | Latest 100 cluster events |
| `GET` | `/kubernetes/namespaces/{namespace}/pods/{pod}/logs?tail=200` | Bounded pod logs |
| `GET` | `/synology/storage` | Configured read-only storage mounts |
| `GET` | `/monitoring/alerts` | Prometheus alerts |
| `GET` | `/monitoring/targets` | Prometheus scrape targets |
| `GET` | `/github/pull-requests` | Open pull requests for configured repositories |
| `GET` | `/radio/status` | Icecast and optional Liquidsoap status |
| `GET` | `/backups/status` | Read-only backup inventory |
| `GET` | `/security/posture` | Local configuration posture findings |
| `POST` | `/automation/plans` | Observe-only remediation plan; body: `{"objective":"..."}` |
| `POST` | `/logs/analyze` | In-memory log analysis; body: `{"logs":"..."}` |
| `POST` | `/incidents/analyze` | Evidence-bound incident report; body: `{"symptoms":"..."}` |
| `GET` | `/history?limit=50` | Latest local chat and incident records |
| `DELETE` | `/history` | Permanently clear local chat and incident records |

Log endpoints accept `tail` from 1 through 1,000 and return no more than
100 KB of text. Kubernetes namespace and pod identifiers, and Docker
container identifiers, are validated before any command is run.

Atlas does not expose mutation endpoints for Docker, Kubernetes, Synology,
GitHub, Prometheus, backups, or radio services. The automation endpoint only
returns proposed actions and required evidence.
