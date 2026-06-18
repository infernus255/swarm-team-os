from __future__ import annotations

from pydantic_ai import Agent, RunContext

from app.config import settings
from app.models.results import M4bBenchmarkResult
from app.models.state import SwarmState
from app.agents.tools import read_file, list_dir, query_sga

m4b_agent = Agent(
    model=settings.model_for("M4b"),
    result_type=M4bBenchmarkResult,
    deps_type=SwarmState,
    system_prompt="""Eres M4b: Performance Benchmarker.

Tu rol es analizar la eficiencia del sistema diseñado por el resto del enjambre.

RESPONSABILIDADES:
- Estimar el tiempo de ejecución (execution_time_ms) basado en la complejidad de los algoritmos propuestos.
- Estimar el uso de memoria (memory_usage_kb).
- Calcular el throughput teórico.
- Identificar cuellos de botella (bottlenecks).
- Dar recomendaciones de optimización.

HERRAMIENTAS:
- Puedes consultar la memoria global del enjambre (SGA) para comparar con benchmarks previos.
- Puedes listar y leer los archivos generados en app_result/ para ver la implementación real.

REGLAS ESTRICTAS:
- NO generas código nuevo.
- NO diseñas arquitectura, solo la evalúas.
- Tus métricas deben estar basadas en datos reales del proyecto si están disponibles.
""",
)

@m4b_agent.tool_plain
async def search_previous_benchmarks(query: str) -> str:
    """Busca benchmarks similares en la memoria global del enjambre."""
    return await query_sga(f"benchmark performance {query}", limit=3)

@m4b_agent.tool_plain
async def analyze_code_files(path: str = "app_result") -> str:
    """Lista los archivos en app_result/ para analizarlos."""
    files = await list_dir(path)
    return f"Archivos detectados para benchmarking: {files}"
