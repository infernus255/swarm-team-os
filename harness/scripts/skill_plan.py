#!/usr/bin/env python3
"""Harness Skill: Plan Updater.
Reads state.json and updates the install plan document with current environment state.
Usage: python harness/scripts/skill_plan.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from utils.state_loader import StateLoader

loader = StateLoader()
REPO_ROOT = loader.repo_root
PLAN_FILE = REPO_ROOT / "docs" / "state_summary.md"


def load_state():
    state = loader.load_state(force_reload=True)
    if not state:
        raise SystemExit(f"No existe {loader.state_file}. Ejecute harness/scripts/skill_state.py primero.")
    return state


def current_environment(state):
    env_id = state.get("current_environment_id")
    environments = state.get("environments", {})
    if env_id and env_id in environments:
        return environments[env_id]
    return state.get("environment", state)


def format_state(state):
    current = current_environment(state)
    hermes = current.get("hermes", {})
    system = current.get("system", {})
    git = current.get("git", {})
    api_keys = current.get("api_keys", {})
    lines = [
        "## 14. Estado actual y validación",
        "",
        "### Entorno actual",
        f"- Environment ID: {current.get('environment', {}).get('environment_id')}",
        f"- Environment type: {current.get('environment', {}).get('env_type')}",
        "",
        "### Hermes",
        f"- Instalado: {hermes.get('installed')}",
        f"- Versión: {hermes.get('version')}",
        f"- Proveedor: {hermes.get('provider')}",
        f"- Modelo por defecto: {hermes.get('model_default')}",
        f"- Base URL: {hermes.get('base_url')}",
        f"- Gateway Telegram: {hermes.get('gateway')}",
        "",
        "### Sistema operativo",
        f"- Nombre: {system.get('os_name')}",
        f"- Versión: {system.get('os_version')}",
        "- Paquetes verificados:",
    ]
    for package in system.get("packages_checked", []):
        lines.append(f"  - {package['package']}: {package['status']}")
    lines += [
        "",
        "### API keys",
        f"- Total de claves detectadas: {api_keys.get('summary', {}).get('total_keys', 0)}",
        f"- Proveedores: {', '.join(api_keys.get('summary', {}).get('providers', []))}",
    ]
    for key in api_keys.get("keys", []):
        limit = key.get("limit") if key.get("limit") is not None else "unknown"
        lines.append(f"  - {key.get('alias')} ({key.get('provider')}): limit={limit}, source={key.get('source')}")
    lines += [
        "",
        "### Repositorio git",
        f"- Rama: {git.get('branch')}",
        f"- Commit: {git.get('commit')}",
        f"- Mensaje: {git.get('message')}",
        f"- Cambios modificados: {git['status'].get('modified', 0)}",
        f"- Archivos no rastreados: {git['status'].get('untracked', 0)}",
        f"- Ahead: {git['status'].get('ahead', 0)}",
        f"- Behind: {git['status'].get('behind', 0)}",
    ]
    return "\n".join(lines) + "\n"


def format_autorunner(state):
    lines = [
        "## 15. Autorunner para IA de bajo tier",
        "",
        "Sigue estos pasos exactos en el orden dado. No hagas suposiciones adicionales.",
        "",
        "1. Actualiza el estado del proyecto:",
        "   - `python3 harness/scripts/skill_state.py`",
        "",
        "2. Actualiza el plan con el estado actual:",
        "   - `python3 harness/scripts/skill_plan.py`",
        "",
        "3. Si hay un nuevo aprendizaje, agrégalo a la memoria:",
        "   - `bash harness/scripts/skill_memory.sh \"Texto del aprendizaje\"`",
        "",
        "4. Sincroniza Docker con el estado del sistema operativo:",
        "   - `python3 harness/scripts/skill_docker.py`",
        "",
        "5. Reconstruye el contenedor para aplicar los cambios:",
        "   - `docker compose build --progress=plain`",
        "",
        "6. Verifica el contenedor y el gateway:",
        "   - `docker compose up -d`",
        "   - `docker compose logs -f`",
        "",
        "Este autorunner está diseñado para ser seguido literalmente por una IA de bajo tier."
    ]
    return "\n".join(lines) + "\n"


def update_plan_file(state):
    state_section = format_state(state)
    autorunner_section = format_autorunner(state)
    
    content = f"# Environment State Summary\n\n{state_section}\n\n{autorunner_section}"
    
    # Ensure docs directory exists
    PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    PLAN_FILE.write_text(content, encoding="utf-8")
    print(f"Plan actualizado en {PLAN_FILE}")


def main():
    state = load_state()
    update_plan_file(state)


if __name__ == "__main__":
    main()
