---
name: skill-commit-push
description: Use this skill to validate the entire harness stack and commit/push changes upstream.
---
# Skill Commit Push
Use this skill when you want to execute all verification checks (OS, docs, Hermes, Copilot, n8n, Docker compose) and push codebase changes to Git.

## How to Use
Run the following Python script from the workspace directory (`/app`):
```bash
python /app/harness/scripts/skill_commit_push.py "Commit message here"
```
This script will execute all validations. If they pass, it will automatically commit and push your changes upstream.
