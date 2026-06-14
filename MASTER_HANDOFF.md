# 🤖 SWARMTEAM OS: MASTER ARCHITECTURE & HANDOFF (v3.0)

> **META-INSTRUCTION FOR ANY AI AGENT (ANTIGRAVITY, COPILOT, HERMES):** 
> This is the ultimate source of truth for the `hermes-swarm` repository. You must adhere to the Spec-Driven Development (SDD) rules, the Poly-Swarm architecture, and the strict Token Efficiency guidelines outlined below. This repo contains BOTH the Jarvis OS logic and the Autonomous Swarm engines. They must learn, self-update, and communicate seamlessly regardless of who or what (User, Hermes, Copilot, Antigravity) triggers them.

---

## 1. THE VISION: DISTRIBUTED, CONCURRENT AGENTic OS
SwarmTeam OS is a multi-instance, distributed operating system. 
- **Hermes (The Runtime):** The underlying agent framework installed on the machine. It receives triggers (CLI, Telegram, Webhook) and executes the Repo.
- **Jarvis (The Intelligence/Dispatcher):** The `jarvis.py` script. It acts as the local brain. **Multiple Jarvis instances can run simultaneously across different nodes** (e.g., one on Oracle handling Telegram, one on the Pentium handling local tasks). They sync via the centralized SGA database and Git.
- **Poly-Swarm (The Workforce):** Specialized engines (`swarm/engines/`) invoked by Jarvis for specific tasks (Copilot, Antigravity, PydanticAI).

---

## 2. HARDWARE TOPOLOGY & MULTI-NODE CAPABILITIES
The system adapts to its environment via `env_drivers/`. Each device has primary roles but can act as a Jarvis instance if needed:

1. **Oracle Cloud (The C2 / Public Gateway):** 
   - **Specs:** ARM Ampere (4 OCPU, 24GB RAM), Ubuntu 24.04.
   - **Capabilities:** Always online Telegram webhook, orchestrator of heavy cloud swarms. The primary "Public Jarvis".
2. **Pentium (The Anchor / Local Mayordomo):**
   - **Specs:** Low-resource local PC, 120GB SSD, Ubuntu Server.
   - **Capabilities:** Hosts the local PostgreSQL+pgvector database (SGA). Runs the OCI Hunter (`cazador.py`). **Can run a local Jarvis instance** optimized for low-resource orchestration, routing heavy tasks to the Ryzen. Functions as the local network gateway/firewall.
3. **Ryzen Desktop (The Muscle / Battle Station):**
   - **Specs:** Ryzen 3600X, RX 5600XT (6GB VRAM), 16GB RAM, 2TB Storage, Windows 11.
   - **Capabilities:** Heavy local compute via Docker (invisible to gaming). Executes local LLM inference (Llama 3), heavy compilation, and media generation. The "Heavy Lifter Jarvis".
4. **Notebook HP (The Mobile Lab / Media Library):**
   - **Specs:** i7 6th Gen, 16GB RAM, NVIDIA 940M, Pop!_OS / CachyOS.
   - **Capabilities:** Portable dev station. Swarm testing ground. Can act as a media server managed by a local Jarvis instance.
5. **Xiaomi 15 Ultra (The Mobile Sensor):**
   - **Capabilities:** Voice commands, mobile dashboard access, biometric authentication for critical Swarm tasks, and fast image processing/vision input for Jarvis.
6. **MX9 Box (The Dashboard / TV Eye):**
   - **Capabilities:** Runs a clean Android TV ROM (e.g., SlimBoxTV). Acts as a visual dashboard for the Swarm OS status and streams media orchestrated by the Notebook/Pentium.
7. **GitHub Codespaces (Ephemeral Dev):**
   - **Capabilities:** Used strictly for rapid IDE modifications to the Jarvis OS itself.

---

## 3. BOOTSTRAPPING, SELF-UPDATING & RUNTIME FLOW

### How Hermes understands the Repo (The Autorunner)
Hermes is a generic agent runtime installed on the OS. It interacts with this repository via the `.clinerules` and execution scripts.
1. **Trigger:** User speaks to Hermes on Telegram or CLI.
2. **Boot:** Hermes reads the repo, identifies `jarvis.py` as the entry point based on `.clinerules` instructions, and executes it.
3. **Context Awareness:** Jarvis uses `env_drivers/` to know *where* it is running (Pentium vs. Oracle) and reads `state.json` via the Harness to understand the global state.

### Self-Updating Code & Swarm Invocation
If the user asks Hermes (or Copilot/Antigravity) to *modify the OS or the Swarm*:
1. The external AI modifies the Python files (`jarvis.py`, `core/`, `swarm/engines/`).
2. The AI uses the Harness Git skills to commit and push.
3. Other active Jarvis instances pull the latest Git changes before their next execution cycle. **The Repo is the source of truth.**

### How Jarvis talks to the Swarm
Jarvis does not hardcode Swarm logic. It uses a dynamic Engine Selector:
1. Jarvis receives a task (e.g., "Build a React app").
2. Jarvis looks in `swarm/engines/` and picks the best tool (e.g., `.swarm_antigravity_sdk`).
3. Jarvis executes the Swarm engine as a sub-process, passing the `application_requirement_prompt.md`.
4. The Swarm generates the app and writes L1 Memory (Technical Insights) to the SGA database.

---

## 4. DUAL-LAYER MEMORY SYSTEM & ALIGNMENT (SGA)
The separation of memory ensures Jarvis and the Swarm don't corrupt each other, while both learning continuously.
- **L0 Memory (Jarvis OS Meta-State):** Managed by Jarvis. Stores node statuses, Telegram conversations, user preferences, and "Which node is currently doing what".
- **L1 Memory (Autonomous Swarm State):** Managed by the Swarm. Stores coding paradigms, bug resolutions, and framework-specific knowledge learned during tasks.
- Both layers live in the **Pentium's PostgreSQL database**, but the repo configuration prevents Swarm tasks from polluting L0 conversational memory.

---

## 5. IMMEDIATE MIGRATION TASKS
1. Move the legacy `.swarm_*` folders from the old repository into `hermes-swarm/swarm/engines/`.
2. Refactor `jarvis.py` to implement the `Engine Selector` logic, allowing it to invoke the newly moved engines.
---

## 8. MULTI-DEVICE STATE TRACKING (`state.json`)
The `state.json` file is the **Global Ledger** of the OS. 
- **Persistence Mandate:** This file MUST NOT be overwritten or wiped. New nodes must be appended to the `environments` dictionary.
- **The Harness:** `harness/scripts/skill_state.py` is the only script authorized to update telemetries automatically.
- **Legacy Context:** The `codespaces-16ec44` entry is the historical birth-node of the system and must be preserved as a reference for future cloud-init setups.

---

## 9. GUARDRAILS FOR AI AGENTS
1. **Never Delete:** Do not delete operational documentation or state history unless explicitly requested.
2. **Context First:** Always read `state.json` before proposing a change to ensure environment compatibility.
3. **Agnostic Communication:** Use the `SGA` (Memory L0/L1) to communicate insights between different nodes and agents.

---
