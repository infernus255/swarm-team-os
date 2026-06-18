# 🗺️ REPO MAP (v4.0)

```
.
├── .agents/
│   └── AGENTS.md                 # Universal AI bootstrap (READ THIS FIRST)
├── config/
│   ├── api_orchestrator.json     # LLM routing configuration
│   └── api_budget.json           # Token spending limits (FinOps)
├── core/
│   ├── config.py                 # Settings, env loading, model tiers
│   ├── orchestrator.py           # GraphRunner (task execution graph)
│   ├── poly_swarm_coordinator.py # Multi-engine task dispatcher
│   ├── engine_selector.py        # LLM-powered engine routing
│   ├── graph.py                  # Node definitions for execution graph
│   └── services/
│       ├── memory_service.py     # Neon DB connector (L0/L1 SGA)
│       └── node_service.py       # Node registration & auditing
├── docs/
│   ├── architecture_insights.md  # Guru-Watch knowledge base
│   ├── copilot-instructions.md   # AI coding rules
│   └── ...                       # Handoffs & plans
├── env_drivers/
│   ├── base_driver.py            # Abstract driver interface
│   ├── codespaces_cloud.py       # GitHub Codespaces adapter
│   ├── local_desktop.py          # Local dev machine adapter
│   └── pentium_mayordomo.py      # Pentium server adapter
├── harness/
│   ├── README.md                 # Skills documentation & troubleshooting
│   ├── collectors/
│   │   └── base.py               # Git & System data collectors
│   ├── docs/
│   │   └── COPILOT_SKILL.md      # AI-agnostic skill reference
│   └── scripts/
│       ├── skill_state.py        # Environment telemetry → state.json
│       ├── skill_memory.py       # Learning entries → memory.md
│       ├── skill_plan.py         # State → install plan update
│       ├── skill_docker.py       # State → Dockerfile sync
│       ├── skill_commit_push.py  # Validated git commit + push
│       ├── skill_env_control.py  # Portable env discovery
│       ├── skill_node_manager.py # Node audit CLI
│       ├── skill_obs_dashboard.py # Live SGA dashboard
│       ├── skill_guru_watch.py   # Upstream knowledge fetcher
│       └── utils/
│           └── state_loader.py   # Shared state I/O + file locking
├── infra/
│   ├── universal-setup.sh        # Cross-platform dependency installer
│   └── db_init.py                # SGA database initializer
├── memory/
│   └── sga_client.py             # Memory proxy for external clients
├── swarm/
│   ├── engines/                  # Specialized execution engines
│   └── blueprints/               # Master prompts for M0-M6 agents
├── tests/                        # Regression test suite
├── jarvis.py                     # Main Jarvis dispatcher
├── MASTER_HANDOFF.md             # Architecture & node topology
├── NEXT_HANDOFF.md               # Roadmap & next steps
├── AI_AUTORUNNER_PROMPT.md       # Copy-paste bootstrap for new AI sessions
├── VERSION                       # Current OS version
├── .clinerules                   # AI coding standards
└── .roomodes                     # Swarm agent role definitions
```
