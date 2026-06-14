#!/usr/bin/env python3
import json
from pathlib import Path
import re

from utils.state_loader import StateLoader

loader = StateLoader()
REPO_ROOT = loader.repo_root
DOCKERFILE = REPO_ROOT / "Dockerfile"


def parse_dockerfile_packages(content):
    if "# PACKAGES-BEGIN" not in content or "# PACKAGES-END" not in content:
        pattern = re.compile(r"apt-get install -y(.*?)(?:\\n|$)", re.S)
        match = pattern.search(content)
        if not match:
            return []
        package_block = match.group(1)
        package_lines = package_block.replace('\\', ' ').split()
        return [pkg.strip() for pkg in package_lines if pkg.strip()]
        
    parts = content.split("# PACKAGES-BEGIN", 1)
    subparts = parts[1].split("# PACKAGES-END", 1)
    packages_block = subparts[0]
    packages = []
    for line in packages_block.splitlines():
        line = line.split("#")[0].replace("\\", "").strip()
        if line:
            packages.append(line)
    return sorted(list(set(packages)))


def update_dockerfile(content, required_packages):
    current = parse_dockerfile_packages(content)
    missing = [pkg for pkg in required_packages if pkg not in current]
    if not missing:
        return content, []
        
    if "# PACKAGES-BEGIN" not in content or "# PACKAGES-END" not in content:
        updated_lines = []
        for line in content.splitlines():
            if "apt-get install -y" in line:
                prefix = line.split("apt-get install -y", 1)[0] + "apt-get install -y"
                updated_lines.append(prefix + " \\")
                for pkg in sorted(set(current + required_packages)):
                    updated_lines.append(f"    {pkg} \\")
            else:
                updated_lines.append(line)
        updated_content = "\n".join(updated_lines) + "\n"
        return updated_content, missing

    parts = content.split("# PACKAGES-BEGIN", 1)
    subparts = parts[1].split("# PACKAGES-END", 1)
    
    lines_before = parts[0].split("\n")
    last_line = lines_before[-1] if lines_before else ""
    indent = " " * (len(last_line) - len(last_line.lstrip(" \t")))
    
    all_packages = sorted(list(set(current + required_packages)))
    package_lines = [f"{indent}# PACKAGES-BEGIN"]
    for pkg in all_packages:
        package_lines.append(f"{indent}{pkg} \\")
    if len(package_lines) > 1:
        package_lines[-1] = package_lines[-1].rstrip(" \\")
    package_lines.append(f"{indent}# PACKAGES-END")
    
    prefix = "\n".join(lines_before[:-1])
    if prefix:
        prefix += "\n"
        
    updated_content = prefix + "\n".join(package_lines) + subparts[1]
    return updated_content, missing


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


def main():
    state = load_state()
    current = current_environment(state)
    required = current.get("system", {}).get("required_packages", [])
    dockerfile_text = DOCKERFILE.read_text(encoding="utf-8")
    updated_text, missing = update_dockerfile(dockerfile_text, required)
    if not missing:
        print(f"Dockerfile ya contiene los paquetes requeridos: {required}")
        return
    DOCKERFILE.write_text(updated_text, encoding="utf-8")
    print(f"Dockerfile actualizado con paquetes adicionales: {missing}")


if __name__ == "__main__":
    main()
