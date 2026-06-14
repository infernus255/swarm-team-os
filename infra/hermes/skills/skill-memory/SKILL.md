---
name: skill-memory
description: Use this skill to append a new lessons-learned or troubleshooting memory entry to the repository.
---
# Skill Memory
Use this skill to record system problems, configuration details, or other learnings in `memory.md` with proper timestamps.

## How to Use
Run the following Bash script from the workspace directory (`/app`) passing the memory text as an argument:
```bash
bash /app/harness/scripts/skill_memory.sh "Your memory entry text here"
```
This will append the new lesson to `memory.md`.
