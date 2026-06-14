# 🗺️ REPO MAP CACHE (v1.0)
# Jarvis: Usa este archivo para conocer la estructura sin listar directorios.

.
├── config/
│   ├── api_orchestrator.json     # Ruteo inteligente de LLMs
│   └── api_budget.json           # Límites de gasto
├── core/
│   ├── graph.py                  # Lógica de estados del Swarm
│   ├── orchestrator.py           # Cerebro de Jarvis
│   └── models.py                 # Contratos Pydantic
├── env_drivers/
│   ├── pentium_mayordomo.py      # Lógica para hardware débil
│   ├── local_desktop.py          # Lógica para Ryzen/Notebook
│   └── codespaces_cloud.py       # Lógica para desarrollo nube
├── harness/
│   ├── scripts/                  # Skills (Git, Docker, Antigravity)
│   └── docs/                     # Reglas SDD
├── infra/
│   ├── universal-setup.sh        # Instalador automático
│   └── hermes/                   # Docker entrypoints
├── memory/
│   └── sga_client.py             # Conector de memoria Postgres
└── swarm/
    └── blueprints/               # Prompts maestros agnósticos
