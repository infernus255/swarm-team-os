from __future__ import annotations

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.agents.registry import build_all_agents
from app.config import settings
from app.engine.orchestrator import orchestrator
from app.engine.workflow import get_dag
from app.models.contracts import CONTRACTS

app = typer.Typer(help="SWARN - Sequential Multi-Agent Pipeline Orchestrator")
console = Console()


@app.command()
def init(
    name: str = typer.Option("MyProject", "--name", "-n", help="Nombre del proyecto"),
    mode: str = typer.Option("greenfield", "--mode", "-m", help="greenfield | brownfield"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Prompt inicial del proyecto"),
):
    """Inicializa un nuevo proyecto SWARN."""
    build_all_agents()
    state = orchestrator.init_project(prompt=prompt, mode=mode, project_name=name)
    dag = get_dag(mode)
    console.print(Panel(f"[bold green]Proyecto '{name}' inicializado[/]"))
    console.print(f"  Modo: {mode}")
    console.print(f"  Primer agente: {dag[0]}")
    console.print(f"  Estado: {state.status.value}")
    console.print(f"  ID: {state.project_id}")


@app.command()
def status():
    """Muestra el estado actual del swarm."""
    state = orchestrator.get_state()
    dag = get_dag(state.workflow_mode)

    table = Table(title="SWARN State")
    table.add_column("Campo", style="bold")
    table.add_column("Valor")

    table.add_row("Proyecto", state.project_id)
    table.add_row("Goal", state.project_goal[:60] + "..." if len(state.project_goal) > 60 else state.project_goal)
    table.add_row("Fase actual", state.current_phase.value)
    table.add_row("Nodo actual", state.currentNode)
    table.add_row("Estado", state.status.value)
    table.add_row("Modo", state.workflow_mode)
    table.add_row("DAG", " -> ".join(dag))
    table.add_row("Errores", str(len(state.errors_encountered)))
    table.add_row("Historial", str(len(state.history)) + " transiciones")

    console.print(table)

    if state.pending_human_review:
        console.print("\n[bold yellow]Pendientes de revision humana:[/]")
        for agent_id in state.pending_human_review:
            console.print(f"  - {agent_id}")


@app.command()
def step(
    agent: str = typer.Argument(..., help="M0, M1, M2, M3, M4, M5, M6"),
    prompt: str = typer.Argument("", help="Prompt/input para el agente"),
):
    """Ejecuta un agente especifico del pipeline."""
    import asyncio

    build_all_agents()
    console.print(f"[bold blue]Ejecutando agente {agent}...[/]")
    try:
        result = asyncio.run(orchestrator.run_agent(agent, prompt))
        console.print(f"[bold green]Agente {agent} completado[/]")
        if "result" in result:
            console.print(json.dumps(result["result"], indent=2, ensure_ascii=False))
        if settings.is_hitl:
            console.print("[yellow]Esperando validacion: swarn validate --approve / --reject[/]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]")


@app.command()
def validate(
    approve: bool = typer.Option(True, "--approve", help="Aprobar el paso"),
    reject: bool = typer.Option(False, "--reject", help="Rechazar el paso"),
    agent: str = typer.Option("", "--agent", "-a", help="ID del agente a validar"),
):
    """Valida (aprueba/rechaza) un paso completado."""
    approved = approve and not reject
    agent_id = agent or orchestrator.state.currentNode
    state = orchestrator.validate_step(agent_id, approved)

    if approved:
        dag = get_dag(state.workflow_mode)
        next_agent = dag[dag.index(agent_id) + 1] if agent_id in dag and dag.index(agent_id) + 1 < len(dag) else None
        if next_agent:
            console.print(f"[green]Paso {agent_id} aprobado. Siguiente: {next_agent}[/]")
            console.print(f"  -> swarn step {next_agent}")
        else:
            console.print(f"[green]Pipeline completado![/]")
    else:
        console.print(f"[yellow]Paso {agent_id} rechazado. Regresando al paso anterior...[/]")


@app.command()
def run():
    """Ejecuta todo el pipeline en modo automatico."""
    import asyncio

    build_all_agents()
    state = orchestrator.get_state()
    dag = get_dag(state.workflow_mode)

    start_idx = dag.index(state.currentNode) if state.currentNode in dag else 0

    for i in range(start_idx, len(dag)):
        agent_id = dag[i]
        console.print(f"\n[bold cyan]==> Ejecutando {agent_id}...[/]")
        try:
            result = asyncio.run(orchestrator.run_agent(agent_id, state.user_prompt))
            console.print(f"[green]OK[/] {agent_id}")
            if i + 1 < len(dag):
                orchestrator.transition(dag[i + 1])
        except Exception as e:
            console.print(f"[bold red]Error en {agent_id}: {e}[/]")
            break

    console.print("\n[bold green]Pipeline completado[/]")


@app.command()
def history():
    """Muestra el historial de transiciones."""
    state = orchestrator.get_state()
    if not state.history:
        console.print("No hay transiciones registradas.")
        return

    table = Table(title="Historial de Transiciones")
    table.add_column("#")
    table.add_column("Desde")
    table.add_column("Hasta")
    table.add_column("Estado")
    table.add_column("Timestamp")

    for i, t in enumerate(state.history, 1):
        table.add_row(
            str(i),
            t.from_phase or "-",
            t.to,
            t.status.value,
            t.timestamp[:19] if t.timestamp else "-",
        )
    console.print(table)


@app.command()
def artifacts():
    """Lista los artefactos generados."""
    artifacts = orchestrator.get_artifacts()
    if not artifacts:
        console.print("No hay artefactos registrados.")
        return

    table = Table(title="Artefactos")
    table.add_column("Agente")
    table.add_column("Ruta")
    for agent_id, path in artifacts.items():
        table.add_row(agent_id, path)
    console.print(table)


@app.command()
def contracts():
    """Muestra los contratos de cada agente."""
    table = Table(title="Contratos de Agentes")
    table.add_column("Agente")
    table.add_column("Rol")
    table.add_column("Inputs")
    table.add_column("Outputs")

    for c in CONTRACTS.values():
        table.add_row(
            c.agent_id,
            c.role[:50] + "...",
            "\n".join(c.input_sources) or "-",
            "\n".join(c.output_paths),
        )
    console.print(table)


if __name__ == "__main__":
    app()
