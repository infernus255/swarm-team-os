---
name: skill-plan
description: Use this skill to synchronize and update the install plan document based on the current state.
---
# Skill Plan
Use this skill to update the master project plan document `docs/HERMES_TELEGRAM_INSTALL_PLAN.md` with the latest system state.

## Prerequisites
You must run `skill-state` first to ensure `/app/state.json` contains current information.

## How to Use
Run the following Python script from the workspace directory (`/app`):
```bash
python /app/harness/scripts/skill_plan.py
```
This script will read the state and rebuild the install plan.
