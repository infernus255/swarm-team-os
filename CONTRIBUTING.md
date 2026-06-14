# Contributing to SwarmTeam OS

This repository is organized around reproducible skills and root-level shared state.

## Recommended workflow

1. Update environment state:
   - `python3 harness/scripts/skill_state.py`
2. Refresh the install plan:
   - `python3 harness/scripts/skill_plan.py`
3. Sync Docker requirements:
   - `python3 harness/scripts/skill_docker.py`
4. Add learning notes:
   - `bash harness/scripts/skill_memory.sh "New learning note"`
5. Validate and commit:
   - `python3 harness/scripts/skill_commit_push.py "My commit message"`

## Notes

- Keep `state.json` at the repository root as the Global Ledger.
- Keep API orchestrator and key limit files in `config/`.
- Do not hand-edit generated docs and state files unless the change is the direct result of the scripts.
