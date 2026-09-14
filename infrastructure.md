infrastructure/

├── README.md
│
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   │
│   ├── frontend/
│   │   └── Dockerfile
│   │
│   ├── ollama/
│   │   └── Dockerfile
│   │
│   ├── postgres/
│   │   └── Dockerfile
│   │
│   └── monitoring/
│       ├── prometheus/
│       └── grafana/
│
├── kubernetes/
│   │
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── backend.yaml
│   │   ├── frontend.yaml
│   │   ├── postgres.yaml
│   │   ├── ollama.yaml
│   │   ├── ingress.yaml
│   │   └── secrets.yaml
│   │
│   ├── monitoring/
│   │   ├── prometheus.yaml
│   │   ├── grafana.yaml
│   │   └── loki.yaml
│   │
│   ├── agents/
│   │   ├── kubernetes-agent.yaml
│   │   ├── docker-agent.yaml
│   │   ├── synology-agent.yaml
│   │   ├── github-agent.yaml
│   │   └── log-agent.yaml
│   │
│   └── environments/
│       ├── dev/
│       ├── test/
│       └── production/
│
├── helm/
│   └── atlas/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── terraform/
│   ├── providers.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── alertmanager/
│
├── storage/
│   ├── pvc/
│   ├── nfs/
│   ├── smb/
│   └── backups/
│
└── ci-cd/
    ├── github-actions/
    ├── build/
    ├── deploy/
    └── release/