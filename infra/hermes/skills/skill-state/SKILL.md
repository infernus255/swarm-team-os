---
name: skill-state
description: Use this skill to synchronize and verify the host system operating state and telemetry.
---
# Skill State
Use this skill when you need to capture the current host operating system state, active processes, and Git repository metadata into `state.json`.

## How to Use
Run the following Python script from the workspace directory (`/app`):
```bash
python /app/harness/scripts/skill_state.py
```
This script will gather telemetry data and update `/app/state.json`.
