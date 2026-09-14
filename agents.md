agents/

├── README.md
│
├── atlas-core/
│   ├── agent.py
│   ├── orchestrator.py
│   ├── dispatcher.py
│   ├── planner.py
│   └── memory.py
│
├── kubernetes-agent/
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.md
│   └── tests/
│
├── docker-agent/
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.md
│   └── tests/
│
├── synology-agent/
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.md
│   └── tests/
│
├── github-agent/
│   ├── agent.py
│   ├── tools.py
│   ├── prompts.md
│   └── tests/
│
├── log-agent/
│   ├── agent.py
│   ├── parsers.py
│   ├── prompts.md
│   └── tests/
│
├── monitoring-agent/
│   ├── agent.py
│   ├── metrics.py
│   ├── alerts.py
│   └── tests/
│
├── backup-agent/
│   ├── agent.py
│   ├── backup.py
│   ├── restore.py
│   └── tests/
│
├── radio-agent/
│   ├── agent.py
│   ├── icecast.py
│   ├── liquidsoap.py
│   ├── prompts.md
│   └── tests/
│
├── security-agent/
│   ├── agent.py
│   ├── scanner.py
│   ├── secrets.py
│   └── tests/
│
├── automation-agent/
│   ├── agent.py
│   ├── workflows.py
│   ├── remediation.py
│   └── tests/
│
└── shared/
    ├── base_agent.py
    ├── models.py
    ├── events.py
    ├── tool_registry.py
    └── prompts.py