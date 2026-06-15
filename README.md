# 🤖 SwarmTeam OS: Elite v3.0

Distributed Agentic OS for Multi-Node Swarms (Poly-Swarm). Optimized for 2026 Agentic Engineering standards, featuring centralized memory alignment (SGA) and autonomous self-improvement.

## 🚀 Vision
SwarmTeam OS is not just a framework; it's a distributed operating system where **Jarvis** (The Dispatcher) orchestrates specialized **Swarm Engines** across multiple hardware nodes (Pentium, Ryzen, Oracle Cloud). It is built on the principles of **Spec-Driven Development (SDD)** and **Harness Engineering**.

## 核心 (Core Components)
- **`core/`**: The brain. Includes `GraphRunner` for cyclic orchestration and `EngineSelector` for dynamic engine invocation.
- **`swarm/blueprints/`**: The "SwarmMaster" prompts and requirement templates.
- **`memory/`**: The **SGA (Shared Global Alignment)** layer, connecting all nodes to a centralized Neon PostgreSQL + pgvector database.
- **`harness/scripts/`**: Deterministic skills for Git, Docker, and the new **Guru-Watch** protocol.

## 📖 Agentic Engineering Bible
The system follows the strict guidelines in `docs/architecture_insights.md`, which integrates best practices from Nous Hermes, Pydantic-AI, and Google Antigravity.

## 🕵️ Guru-Watch Protocol
SwarmTeam OS is self-updating. Via `harness/scripts/skill_guru_watch.py`, the system autonomously:
1. Crawls industry leader repositories for latest best practices.
2. Indexes insights into the **SGA L1 Knowledge Layer**.
3. Updates core architectural guidelines to prevent obsolescence.

## 🛠️ Quick Start
1. **Initialize Environment:**
   ```bash
   bash infra/universal-setup.sh
   ```
2. **Configure SGA:** Set your `DATABASE_URL` in `hermes.env`.
3. **Run Jarvis:**
   ```bash
   python jarvis.py "Your request here"
   ```

## 🛡️ Regression Control
Every core change is validated against `tests/test_swarm_core.py` to ensure architectural integrity and prevent regressions in the dispatcher logic.

---
*SwarmTeam OS: The future of autonomous, distributed intelligence.*
