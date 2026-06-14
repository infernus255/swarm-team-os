---
name: skill-docker
description: Use this skill to synchronize the container Dockerfile dependencies with detected system requirements.
---
# Skill Docker
Use this skill to ensure that all required system packages from the current state are declared in the Dockerfile.

## Prerequisites
You must run `skill-state` first to generate `/app/state.json`.

## How to Use
Run the following Python script from the workspace directory (`/app`):
```bash
python /app/harness/scripts/skill_docker.py
```
This script will adjust packages in the Dockerfile if needed.
