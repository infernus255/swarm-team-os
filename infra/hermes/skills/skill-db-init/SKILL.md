---
name: skill-db-init
description: Use this skill to initialize the central Neon cloud database schema, vector extensions, and node tables.
---
# Skill DB Init
Use this skill to initialize the database tables and register the node (`ryzen_muscle`) in the Neon Postgres instance.

## How to Use
Run the following Python script from the workspace directory (`/app`):
```bash
python /app/infra/db_init.py
```
This script will setup the database schemas and initialize Neon for the swarm nodes.
