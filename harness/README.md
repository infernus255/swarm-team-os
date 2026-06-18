# Harness Skills

Deterministic CLI tools for maintaining state, memory, plans, and Docker sync across all environments.
These scripts are the **single source of truth** — prefer running them over manual file edits.

## Prerequisites

- Python 3.10+ (use `python` on Windows, `python3` on Linux/macOS)
- For database-dependent skills: `DATABASE_URL` env var (Neon PostgreSQL)
- Run all commands from the **repository root**

## Available Skills

### Core Skills (zero dependencies beyond Python stdlib)

| Skill | Command | What it does |
|---|---|---|
| State Collector | `python harness/scripts/skill_state.py` | Scans OS, git, API keys → writes `state.json` |
| Memory Writer | `python harness/scripts/skill_memory.py "text"` | Appends timestamped learning entry to `memory.md` |
| Plan Updater | `python harness/scripts/skill_plan.py` | Updates install plan doc from `state.json` |
| Docker Sync | `python harness/scripts/skill_docker.py` | Syncs Dockerfile packages with required packages from `state.json` |
| Commit & Push | `python harness/scripts/skill_commit_push.py "msg"` | Validates state then commits + pushes |
| Env Control | `python harness/scripts/skill_env_control.py` | Portable environment discovery & sync |

### Extended Skills (require external dependencies)

| Skill | Command | Dependencies |
|---|---|---|
| Node Manager | `python harness/scripts/skill_node_manager.py {info\|register\|check}` | `core.services.node_service` |
| Dashboard | `python harness/scripts/skill_obs_dashboard.py --mode summary` | `psycopg2`, `python-dotenv`, `DATABASE_URL` |
| Guru Watch | `python harness/scripts/skill_guru_watch.py` | `requests`, `core.services.memory_service` |
| Review Package | `python harness/scripts/skill_generate_ai_review_package.py` | None (generates markdown) |

## Recommended Workflow

```bash
# 1. Collect state (always do this first)
python harness/scripts/skill_state.py

# 2. Update plan from state
python harness/scripts/skill_plan.py

# 3. Sync Docker if on Linux
python harness/scripts/skill_docker.py

# 4. Record any learnings
python harness/scripts/skill_memory.py "What I learned"

# 5. Validate and commit
python harness/scripts/skill_commit_push.py "Description of changes"
```

## Commit & Push Modes

```bash
# Default: core validations block, non-critical are warnings
python harness/scripts/skill_commit_push.py "my changes"

# Force: skip all validations
python harness/scripts/skill_commit_push.py --force "emergency fix"

# Strict: all validations must pass (Hermes, n8n, Docker, etc.)
python harness/scripts/skill_commit_push.py --strict "production release"
```

## Troubleshooting

| Problem | Solution |
|---|---|
| `UnicodeEncodeError` on Windows | Scripts auto-fix to UTF-8. If still failing, set `PYTHONIOENCODING=utf-8` |
| `DATABASE_URL not found` | Set it in `.env` or `hermes.env` for dashboard/guru-watch |
| `state.json not found` | Run `python harness/scripts/skill_state.py` first |
| `ModuleNotFoundError` | Run from the repository root directory |

## Engineering Principles

- **Deterministic:** Scripts read real system state, never guess or infer.
- **Portable:** Works on Windows, Linux, macOS, Docker, and Codespaces.
- **Idempotent:** Safe to run multiple times without side effects.
- **Composable:** Each skill does one thing well. Chain them in workflows.
