animated-invention/

├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml
├── .env.example
│
├── docs/
│   ├── PROJECT_ATLAS_MASTER_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── DEPLOYMENT.md
│   ├── API_REFERENCE.md
│   └── TROUBLESHOOTING.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   ├── schemas/
│   │   │   └── middleware/
│   │   │
│   │   ├── services/
│   │   │   ├── ollama_service.py
│   │   │   ├── docker_service.py
│   │   │   ├── kubernetes_service.py
│   │   │   ├── synology_service.py
│   │   │   └── github_service.py
│   │   │
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── tools/
│   │   └── utils/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── assets/
│   │
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── agents/
│   ├── kubernetes-agent/
│   │   ├── agent.py
│   │   ├── tools.py
│   │   └── prompts.md
│   │
│   ├── docker-agent/
│   ├── synology-agent/
│   ├── github-agent/
│   ├── monitoring-agent/
│   ├── log-agent/
│   └── automation-agent/
│
├── prompts/
│   ├── system/
│   │   ├── atlas-core.md
│   │   ├── kubernetes-agent.md
│   │   ├── docker-agent.md
│   │   ├── synology-agent.md
│   │   └── github-agent.md
│   │
│   ├── workflows/
│   │   ├── root-cause-analysis.md
│   │   ├── remediation.md
│   │   └── incident-analysis.md
│   │
│   └── examples/
│
├── infrastructure/
│   ├── docker/
│   │   ├── backend/
│   │   ├── frontend/
│   │   └── ollama/
│   │
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── backend.yaml
│   │   ├── frontend.yaml
│   │   ├── ollama.yaml
│   │   ├── postgres.yaml
│   │   └── ingress.yaml
│   │
│   ├── helm/
│   │   └── atlas/
│   │
│   └── terraform/
│
├── scripts/
│   ├── bootstrap.sh
│   ├── install.sh
│   ├── backup.sh
│   ├── restore.sh
│   ├── healthcheck.sh
│   └── deploy.sh
│
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── dashboards/
│
├── data/
│   ├── vectorstore/
│   ├── backups/
│   └── cache/
│
└── examples/
    ├── docker-compose/
    ├── kubernetes/
    └── agent-configs/