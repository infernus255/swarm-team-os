from __future__ import annotations

import os
import datetime
import typer
from app.config import settings
from app.engine.orchestrator import SwarmOrchestrator

cli = typer.Typer(name="swarm-antigravity", help="CLI para interactuar con el Swarm de Google Antigravity SDK")


@cli.command()
def init(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Requerimiento o idea inicial del proyecto"),
    mode: str = typer.Option("hitl", "--mode", "-m", help="Modo del enjambre: hitl o auto"),
):
    """Inicializa la estructura de directorios y el manifiesto inicial en app_result."""
    settings.swarm_mode = mode
    orchestrator = SwarmOrchestrator()
    
    print("[*] Inicializando nuevo proyecto...")
    if not orchestrator.preflight_check():
        print("[⚠️] Advertencia: El pre-flight check falló. Verifique sus claves de API.")
    
    # Crear estructura básica en app_result
    result_dir = settings.result_dir
    for sub in ["src", "deploy", "docs", "tdp", "bsp", "architecture", "tests/specs"]:
        (result_dir / sub).mkdir(parents=True, exist_ok=True)
    
    # Escribir manifiesto base
    manifest_content = f"# Project Manifest\n\n- **Prompt Inicial:** {prompt}\n- **Estado:** INICIALIZADO\n- **Fecha:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    (result_dir / "PROJECT_MANIFEST.md").write_text(manifest_content, encoding="utf-8")
    
    # Escribir memoria inicial
    (result_dir / "MEMORY.md").write_text("# Memoria Histórica del Proyecto\n\n- Proyecto inicializado exitosamente.", encoding="utf-8")
    
    print(f"[✓] Estructura creada en {settings.result_dir}")
    print("[✓] Manifiesto del proyecto y MEMORY.md creados con éxito.")


@cli.command()
def run(
    agent_id: str = typer.Argument(default="all", help="ID del agente a ejecutar (M0-M6) o 'all' para todo el flujo"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Prompt para el agente"),
):
    """Ejecuta un agente específico o todo el flujo dependiendo del modo."""
    orchestrator = SwarmOrchestrator()
    import asyncio
    
    async def _async_run():
        if agent_id == "all" or settings.swarm_mode == "auto":
            print("[*] Iniciando modo AUTORUNNER...")
            agents = ["M0", "M1", "M2", "M2.5", "M3", "M4", "M4b", "M5", "M6"]
            for agent in agents:
                print(f"\n--- Ejecutando {agent} ---")
                res = await orchestrator.run_agent(agent, prompt)
                if res['status'] != "DONE":
                    print(f"[❌] Error en {agent}. Deteniendo Autorunner.")
                    break
            print("\n[✓] Proyecto finalizado por el Swarm Autónomo.")
        else:
            print(f"[*] Iniciando modo HITL para {agent_id}...")
            res = await orchestrator.run_agent(agent_id, prompt)
            print(f"[✓] Resultados de ejecución: {res['status']}")
            if "action_required" in res:
                print(f"[⚠️] Atención: {res['action_required']}")
                print(f"Prompt a correr manualmente:\n{res['prompt_to_run']}")
            print("\n[?] ¿Aprobado? (Y/N/Feedback) - El humano debe validar antes de avanzar.")
            
    asyncio.run(_async_run())


@cli.command()
def check():
    """Valida la paridad código-especificación (Anti-Drift) y realiza pre-flight check de modelos."""
    orchestrator = SwarmOrchestrator()
    print("[*] Ejecutando Pre-flight check...")
    if orchestrator.preflight_check():
        print("[✓] Pre-flight check completado exitosamente.")
    else:
        print("[❌] Pre-flight check fallido.")

    print("[*] Validando desviación (spec-drift) entre código y especificaciones...")
    if orchestrator.check_spec_drift():
        print("[✓] Todo en orden. No se detectaron desviaciones.")
    else:
        print("[❌] Desviación detectada. Regrese el flujo a M2/M3 para corregir.")


if __name__ == "__main__":
    cli()
