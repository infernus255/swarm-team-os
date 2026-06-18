#!/usr/bin/env python3
"""Harness Skill: Validated Commit & Push.
Runs validation checks before committing and pushing. Non-critical validations (Hermes, n8n, Copilot docs)
are treated as warnings unless --strict mode is used. Core validations (state.json, git) always block.
Usage: python harness/scripts/skill_commit_push.py [--force] [--strict] "Commit message"
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from utils.state_loader import StateLoader

loader = StateLoader()
REPO_ROOT = loader.repo_root


def run(cmd, check=True, capture_output=True):
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=True, encoding="utf-8", errors="replace")


def validate_file(path):
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return False, f"Falta el archivo requerido: {path}"
    if file_path.stat().st_size == 0:
        return False, f"El archivo {path} está vacío"
    return True, None


def load_state():
    state = loader.load_state(force_reload=True)
    if not state:
        return None, "No se encontró state.json. Ejecuta harness/scripts/skill_state.py primero."
    return state, None


def current_state_entry(state):
    env_id = state.get("current_environment_id")
    environments = state.get("environments", {})
    if env_id and env_id in environments:
        return environments[env_id]
    return state.get("environment", state)


def validate_os(state):
    current = current_state_entry(state)
    system = current.get("system", {})
    if not system.get("os_name"):
        return False, "No se detectó el nombre del sistema operativo en state.json"
    missing = [pkg["package"] for pkg in system.get("packages_checked", []) if pkg["status"] != "installed"]
    if missing:
        return False, f"Paquetes faltantes o no instalados: {', '.join(missing)}"
    return True, None


def validate_hermes(state):
    current = current_state_entry(state)
    hermes = current.get("hermes", {})
    if not hermes.get("installed"):
        return False, "Hermes no está instalado según state.json"
    if not hermes.get("provider") or not hermes.get("model_default") or not hermes.get("base_url"):
        return False, "La configuración de Hermes no está completa en state.json"
    if shutil.which("hermes"):
        try:
            result = run(["hermes", "config", "show"], check=False)
            if result.returncode != 0:
                return False, "El binario Hermes existe pero no se pudo ejecutar 'hermes config show'"
        except Exception as exc:
            return False, f"Error al ejecutar Hermes: {exc}"
    return True, None


def validate_agent_docs():
    docs = [
        (".agents/AGENTS.md", ["Universal AI bootstrap", "skill_state.py", "skill_plan.py", "skill_commit_push.py"]),
    ]
    for path, phrases in docs:
        file_path = REPO_ROOT / path
        if not file_path.exists():
            return False, f"Falta el bootstrap AI universal: {path}"
        content = file_path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in content:
                return False, f"El archivo {path} no menciona '{phrase}'"
    return True, None


def validate_n8n():
    if not (REPO_ROOT / "docs" / "N8N.md").exists():
        return False, "Falta la documentación de n8n: docs/N8N.md"
    
    # If running inside a container, check reachability of 'n8n' service
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect(("n8n", 5678))
            s.close()
            return True, None
        except Exception as exc:
            return False, f"n8n no es accesible en la red del contenedor: {exc}"

    # Check if n8n is running locally or in Docker
    local_n8n = shutil.which("n8n")
    if local_n8n:
        if shutil.which("pgrep"):
            proc = run(["pgrep", "-f", "n8n"], check=False)
            if proc.returncode != 0:
                return False, "n8n no parece estar levantado en el sistema local"
        return True, None
        
    # If not local, check if running in docker
    if shutil.which("docker"):
        try:
            # Check if n8n service is running or configured in docker compose
            config_proc = run(["docker", "compose", "config", "--services"], check=False)
            if config_proc.returncode == 0 and "n8n" in config_proc.stdout.splitlines():
                ps_proc = run(["docker", "compose", "ps"], check=False)
                if ps_proc.returncode == 0 and "n8n" in ps_proc.stdout.lower():
                    # Check if status indicates it is up/running
                    if any(status in ps_proc.stdout.lower() for status in ["up", "running", "running (healthy)"]):
                        return True, None
                return False, "n8n está configurado en docker-compose, pero el contenedor no está iniciado (ejecuta docker compose up -d)"
        except Exception as exc:
            return False, f"Error al verificar n8n en Docker: {exc}"
            
    return False, "n8n no está instalado en el PATH local ni corriendo en Docker"


def validate_api_keys(state):
    current = current_state_entry(state)
    api_keys = current.get("api_keys", {}).get("keys", [])
    if not api_keys:
        return False, "No se detectaron claves API en state.json. Ejecuta harness/scripts/skill_state.py con las claves definidas."
    missing = [key for key in api_keys if key.get("limit") is None]
    if missing:
        aliases = [key.get("alias") or key.get("key_id", "unknown") for key in missing]
        return False, f"Faltan límites para las claves API: {', '.join(aliases)}"
    return True, None


def validate_docker():
    dockerfile = REPO_ROOT / "Dockerfile"
    if not dockerfile.exists():
        return False, "Falta Dockerfile"
    
    # If running inside a container, skip docker binary/daemon verification
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        if not (REPO_ROOT / "docker-compose.yml").exists():
            return False, "Falta docker-compose.yml"
        return True, None

    if not shutil.which("docker"):
        return False, "docker no está instalado en el PATH"
    try:
        result = run(["docker", "compose", "config"], check=False)
        if result.returncode != 0:
            return False, "docker compose config falló, revisa docker-compose.yml"
    except Exception as exc:
        return False, f"Error al ejecutar docker compose config: {exc}"
    return True, None


def git_add_commit_push(message):
    run(["git", "add", "."])
    run(["git", "commit", "-m", message])
    run(["git", "push"])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validated commit and push")
    parser.add_argument("--force", action="store_true", help="Skip all validations and commit directly")
    parser.add_argument("--strict", action="store_true", help="Treat all validations as blocking (default: only core validations block)")
    parser.add_argument("message", nargs="*", default=["Auto commit: harness validated"], help="Commit message")
    args = parser.parse_args()
    commit_message = " ".join(args.message)

    loader.acquire_lock()
    try:
        if args.force:
            print("[Force] Skipping all validations...")
            git_add_commit_push(commit_message)
            print("Commit y push completados (force mode).")
            return

        # Core validations (always blocking)
        core_errors = []
        state, err = load_state()
        if err:
            core_errors.append(err)

        for path in ["state.json", "memory.md", "README.md"]:
            ok, msg = validate_file(path)
            if not ok:
                core_errors.append(msg)

        # Non-critical validations (warnings unless --strict)
        warnings = []
        if state:
            for validator, label in [
                (lambda: validate_os(state), "OS"),
                (lambda: validate_hermes(state), "Hermes"),
                (lambda: validate_agent_docs(), "Agent docs"),
                (lambda: validate_api_keys(state), "API keys"),
                (lambda: validate_n8n(), "n8n"),
                (lambda: validate_docker(), "Docker"),
            ]:
                ok, msg = validator()
                if not ok:
                    if args.strict:
                        core_errors.append(f"[{label}] {msg}")
                    else:
                        warnings.append(f"[{label}] {msg}")

        # Report
        if warnings:
            print("\nWarnings (non-blocking):")
            for w in warnings:
                print(f"  - {w}")

        if core_errors:
            print("\nCore validation failed:")
            for e in core_errors:
                print(f"  - {e}")
            sys.exit(1)

        print("\nCore validations passed. Committing...")
        git_add_commit_push(commit_message)
        print("Commit y push completados.")
    finally:
        loader.release_lock()


if __name__ == "__main__":
    main()
