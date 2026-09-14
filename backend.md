backend/

├── README.md
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── chat.py
│   │   │   ├── kubernetes.py
│   │   │   ├── docker.py
│   │   │   ├── synology.py
│   │   │   ├── github.py
│   │   │   └── monitoring.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   ├── system.py
│   │   │   └── alerts.py
│   │   │
│   │   └── middleware/
│   │       ├── logging.py
│   │       └── auth.py
│   │
│   ├── services/
│   │   ├── ollama_service.py
│   │   ├── kubernetes_service.py
│   │   ├── docker_service.py
│   │   ├── synology_service.py
│   │   ├── github_service.py
│   │   └── monitoring_service.py
│   │
│   ├── agents/
│   │   ├── atlas_agent.py
│   │   ├── kubernetes_agent.py
│   │   ├── docker_agent.py
│   │   ├── synology_agent.py
│   │   ├── github_agent.py
│   │   └── log_agent.py
│   │
│   ├── repositories/
│   │   ├── chat_repository.py
│   │   ├── alert_repository.py
│   │   └── config_repository.py
│   │
│   ├── models/
│   │   ├── chat.py
│   │   ├── alert.py
│   │   └── settings.py
│   │
│   ├── prompts/
│   │   ├── atlas_system.md
│   │   ├── kubernetes_agent.md
│   │   ├── docker_agent.md
│   │   ├── synology_agent.md
│   │   └── root_cause_analysis.md
│   │
│   └── utils/
│       ├── logger.py
│       ├── security.py
│       ├── parser.py
│       └── helpers.py
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/