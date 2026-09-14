Create the complete Agents layer for Project Atlas.

Requirements:

Create a modular multi-agent architecture.

Agents:

- Atlas Core Agent
- Kubernetes Agent
- Docker Agent
- Synology Agent
- GitHub Agent
- Log Agent
- Monitoring Agent
- Backup Agent
- Radio Agent
- Security Agent
- Automation Agent

Requirements:

1. Shared BaseAgent class.

2. Tool registry.

3. Async architecture.

4. Agent orchestration.

5. Tool calling support.

6. Ollama integration.

7. Structured responses.

8. Root-cause-analysis workflows.

9. Extensible plugin architecture.

10. Production quality logging.

Generate:

agent.py
tools.py
prompts.md
tests/

for every agent.

Create orchestration layer capable of selecting multiple agents for one task.

Example:

User:
"Waarom werkt mijn stream niet?"

Atlas Core
→ Kubernetes Agent
→ Log Agent
→ Radio Agent
→ Ollama Analysis

Generate maintainable production-ready code.