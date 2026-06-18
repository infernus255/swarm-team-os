# Harness Skill Documentation (AI-Agnostic)

These scripts are designed as deterministic skills for maintaining project state, learning, plan updates, and Docker synchronization. They work with **any AI agent** — not just Copilot.

## Available skills

- `python harness/scripts/skill_state.py`
  - Gathers actual system and repo status.
  - Writes `state.json` from current machine state.
  - Records environment-specific state so this repo can learn from each environment independently.
  - Detects multiple API keys and tracks their configured limits.
  - Does not guess configuration; it reads OS and git directly.

- `python harness/scripts/skill_plan.py`
  - Reads `state.json` and updates `docs/HERMES_TELEGRAM_INSTALL_PLAN.md`.
  - Inserts the current state section and a low-tier autorunner block.
  - Keeps the install plan reproducible and aligned with the current environment.

- `python harness/scripts/skill_docker.py`
  - Reads `state.json` and synchronizes `Dockerfile` package installation with required packages.
  - Ensures the Docker build is consistent with the detected system state.

- `python harness/scripts/skill_memory.py "Learning text"`
  - Appends a timestamped learning entry to `memory.md`.
  - No state inference; only writes the provided text.

- `python harness/scripts/skill_commit_push.py [--force] [--strict] "Commit message"`
  - Validates state, docs, and infrastructure.
  - Default mode: core validations block, non-critical show warnings.
  - `--force`: skip all validations and commit directly.
  - `--strict`: all validations must pass.

- `python harness/scripts/skill_env_control.py`
  - Portable environment discovery and state synchronization.

- `python harness/scripts/skill_node_manager.py {info|register|check}`
  - Node registration, dependency audit, and centralized config check.

- `python harness/scripts/skill_obs_dashboard.py --mode {summary|nodes|projects|knowledge}`
  - Real-time observability dashboard (requires DATABASE_URL).

## Engineering principles

- Use scripts as deterministic tools.
- Avoid making ad hoc file edits when these scripts are available.
- Prefer concrete command execution over speculative AI changes.
- Maintain reproducibility across different AI sessions and platforms.
- Use `python` (not `python3`) for cross-platform compatibility.

## Example usage

- To refresh project status:
  - `python harness/scripts/skill_state.py`
- To refresh the install plan:
  - `python harness/scripts/skill_plan.py`
- To add a learning entry:
  - `python harness/scripts/skill_memory.py "Detected missing npm package in environment"`
- To sync Docker with required packages:
  - `python harness/scripts/skill_docker.py`
- To commit with force mode:
  - `python harness/scripts/skill_commit_push.py --force "emergency hotfix"`
