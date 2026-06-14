# Arquitectura del Enjambre (Template)

## Visión General
El enjambre sigue una arquitectura **Cloud-First/API-Driven** diseñada para ejecución determinista.

## Modelo de Orquestación (DAG)
El flujo de agentes sigue un Grafo Acíclico Dirigido:
`M0 (Bootstrapper)` -> `M1 (TDP)` -> `M2 (BSP)` -> `M3 (Arch)` -> `M4 (QA)` -> `M5 (Code)` -> `M6 (Deploy)`

## Especificaciones Técnicas
- **Estado:** Gestionado en `.swarn/states/swarm_state.json`.
- **Harness:** Scripts estáticos en `scripts/` (Node.js).
- **Contratos:** Definidos en `.swarn/specs/CONTRACTS.md`.

## Flujo de Trabajo
1. **Modo HITL (Pausado):** Cada transición requiere validación `Y/N`.
2. **Modo Autónomo:** Ejecuta `default_swarm_auto_runner.js` utilizando la lógica del orquestador de estados para pasar de un agente al siguiente sin intervención manual, validando los contratos automáticamente.
