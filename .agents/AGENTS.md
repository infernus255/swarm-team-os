# SwarmTeam OS — Agent Bootstrap (v4.0)

> **What is this?** This is a distributed Agentic Operating System. If you are an AI agent
> (Antigravity, Gemini CLI, Copilot, Codex, OpenCode, Hermes, Pydantic, Cursor, or any other),
> read this file FIRST before doing anything in this repository.

## Quick Start (mandatory first steps)

```bash
# 1. Collect environment state (deterministic — no AI inference)
python harness/scripts/skill_state.py

# 2. Read the generated state to understand where you are
# (look at state.json — it tells you OS, git branch, environment ID)

# 3. Read MASTER_HANDOFF.md for full architecture context
```

## Project Structure

```
.
├── .agents/AGENTS.md         # THIS FILE — universal AI bootstrap
├── jarvis.py                 # Main entry point (The Intelligence/Dispatcher)
├── core/
│   ├── config.py             # Settings, env loading, model tiers
│   ├── orchestrator.py       # GraphRunner (task execution graph)
│   ├── poly_swarm_coordinator.py  # Multi-engine task dispatcher
│   ├── engine_selector.py    # LLM-powered engine routing
│   └── services/
│       ├── memory_service.py # Neon PostgreSQL + pgvector (L0/L1 memory)
│       └── node_service.py   # Node registration & dependency auditing
├── harness/
│   ├── scripts/              # Deterministic CLI skills (see below)
│   └── collectors/           # System & git data collectors
├── swarm/
│   ├── engines/              # Specialized execution engines
│   └── blueprints/           # Master prompts for swarm agents
├── env_drivers/              # Environment-specific adapters
├── infra/                    # Docker, DB init, setup scripts
├── memory/                   # SGA client proxy
├── docs/                     # Architecture docs, handoffs, plans
└── tests/                    # Regression test suite
```

## Harness Skills (deterministic tools — use these, don't edit files manually)

| Skill | Command | Purpose |
|---|---|---|
| **State Collector** | `python harness/scripts/skill_state.py` | Scans OS, git, API keys → writes `state.json` |
| **Memory Writer** | `python harness/scripts/skill_memory.py "learning text"` | Appends timestamped entry to `memory.md` |
| **Plan Updater** | `python harness/scripts/skill_plan.py` | Updates install plan from `state.json` |
| **Docker Sync** | `python harness/scripts/skill_docker.py` | Syncs Dockerfile packages with `state.json` |
| **Commit & Push** | `python harness/scripts/skill_commit_push.py "message"` | Validates state + commits + pushes |
| **Env Control** | `python harness/scripts/skill_env_control.py` | Portable environment sync |
| **Node Manager** | `python harness/scripts/skill_node_manager.py {info\|register\|check}` | Node audit & registration |
| **Dashboard** | `python harness/scripts/skill_obs_dashboard.py --mode summary` | Live SGA observability (requires DB) |
| **Guru Watch** | `python harness/scripts/skill_guru_watch.py` | Fetches upstream architecture insights |

> **Note:** Use `python` (not `python3`). On systems where only `python3` exists, alias accordingly.

## Operating Rules

1. **Read before writing.** Always read `state.json` and `MASTER_HANDOFF.md` before proposing changes.
2. **Use harness skills.** Don't manually edit `state.json`, `memory.md`, or `Dockerfile`. Use the scripts above.
3. **No product code in core.** The `core/` directory is for the OS framework only. Application code goes in `app_result/`.
4. **Never delete state.** The `state.json` ledger must never be overwritten or deleted. New environments are appended to the `environments` dictionary.
5. **Regression gate.** Changes to `core/` must pass `tests/test_swarm_core.py`.
6. **Domain isolation.** When writing to memory (SGA), always tag with the correct domain: `game`, `swarm`, `harness`, or `system`.
7. **Commit discipline.** Use `python harness/scripts/skill_commit_push.py "message"` instead of raw git commands when possible.

## Architecture Overview

- **Hermes** = Runtime agent framework (CLI/Telegram triggers)
- **Jarvis** = `jarvis.py` — the local intelligence dispatcher
- **Poly-Swarm** = Multi-engine coordinator in `swarm/engines/`
- **SGA** = Swarm Global Archive — dual-layer memory in Neon PostgreSQL
  - L0: Project context & node state
  - L1: Autonomous swarm knowledge (vectorized with pgvector)
- **Harness** = Deterministic skill scripts for reproducible operations

## Notification System

After task completion, Jarvis sends a notification via [ntfy.sh](https://ntfy.sh):
- Topic: `jarvis_os` (configurable via `NTFY_TOPIC` env var)
- Integrated in `jarvis.py` → `_send_notification()` method
- Manual test: `curl -d "test message" ntfy.sh/jarvis_os`

## Key Files for Context

| File | Purpose |
|---|---|
| `MASTER_HANDOFF.md` | Full architecture & node topology |
| `NEXT_HANDOFF.md` | Roadmap & next steps |
| `AI_AUTORUNNER_PROMPT.md` | Copy-paste bootstrap prompt for new AI sessions |
| `repo_map.md` | Compact directory map |
| `VERSION` | Current OS version |
| `.clinerules` | Coding standards for AI agents |
| `.roomodes` | Swarm agent role definitions (M0-M6) |
