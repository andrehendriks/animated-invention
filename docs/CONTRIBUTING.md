# Contributing guide

## Prerequisites

- Python 3.12
- Node.js 22
- Docker with Docker Compose v2
- Optional: an Ollama instance for interactive chat testing

## Local development

Run the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run the frontend in another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Use Docker Compose for integrated testing:

```powershell
docker compose up --build
```

## Project boundaries

- `backend/app/api`: HTTP routes, validation, authentication boundaries.
- `backend/app/services`: integration and domain operations.
- `backend/app/agents`: evidence collection and agent orchestration.
- `frontend/src`: dashboard UI and typed API client.
- `infrastructure`: Prometheus, Grafana, and Kubernetes resources.
- `scripts`: repeatable local deployment and verification tooling.
- `docs`: user, operational, and technical documentation.

Keep integrations read-only unless a separately designed, authorized execution
model is introduced. Validate external identifiers before invoking Docker or
Kubernetes clients. Do not put secrets in source, tests, fixtures, or docs.

## Testing

Backend tests:

```powershell
docker build --tag atlas-backend-test .\backend
docker run --rm atlas-backend-test pytest -q
```

Frontend tests:

```powershell
docker build --target test --tag atlas-frontend-test .\frontend
```

Integrated runtime check:

```powershell
.\scripts\smoke-compose.ps1
```

Use custom smoketest ports if a local Atlas deployment occupies its defaults.

## Change expectations

1. Keep changes focused and preserve existing behavior.
2. Add or update tests for behavior changes.
3. Update directly related documentation and `.env.example` for new
   configuration.
4. Run the smallest relevant test suite before opening a pull request.
5. Describe user-visible behavior, configuration changes, and validation in
   the pull request.

## Adding an integration

New integrations should:

1. Use a dedicated service class with typed output models.
2. Have an explicit `ATLAS_*_ENABLED` switch.
3. Use read-only credentials and operations by default.
4. Return clear failures rather than silently falling back.
5. Be covered by unit tests and included in health/configuration documentation.
6. Be added to the agent orchestration only when it provides relevant evidence.

## Documentation

Keep the following documents aligned with the implementation:

- [CONFIGURATION.md](CONFIGURATION.md) for environment variables.
- [USER_ADMIN_GUIDE.md](USER_ADMIN_GUIDE.md) for daily operation.
- [RUNBOOKS.md](RUNBOOKS.md) for incident response.
- [SECURITY.md](SECURITY.md) for exposure and credential guidance.
- [INTEGRATIONS.md](INTEGRATIONS.md) for integration setup.
- [BACKUP_AND_RECOVERY.md](BACKUP_AND_RECOVERY.md) for persistent data.
