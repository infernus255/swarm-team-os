# 🗺️ REPO MAP ELITE (v3.0)

.
├── config/
│   ├── api_orchestrator.json     # Ruteo inteligente de LLMs
│   └── api_budget.json           # Límites de gasto (FinOps)
├── core/
│   ├── orchestrator.py           # Brain (GraphRunner + SGA Sync)
│   ├── engine_selector.py        # Dispatcher de Motores Poly-Swarm
│   ├── graph.py                  # Definición de Nodos del Grafo
│   └── services/
│       └── memory_service.py     # Conector Neon DB (L0/L1)
├── docs/
│   ├── architecture_insights.md  # La Biblia Agéntica (Guru-Watch)
│   └── ...                       # Handoffs y Guías
├── harness/
│   └── scripts/
│       ├── skill_guru_watch.py   # Auto-update de conocimiento
│       ├── skill_state.py        # Telemetría de hardware
│       └── ...                   # Skills Git/Docker
├── infra/
│   ├── universal-setup.sh        # Instalador agnóstico
│   └── db_init.py                # Inicializador SGA
├── memory/
│   └── sga_client.py             # Proxy de memoria core
├── swarm/
│   ├── engines/                  # Workforce (Motores especializados)
│   └── blueprints/               # Master Prompts (v3.0)
└── tests/                        # Regression Control Suite
