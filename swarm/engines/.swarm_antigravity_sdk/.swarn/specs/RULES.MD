# Swarm General Rules & Spec-Driven Development (SDD) Guidelines

Este documento establece las políticas de desarrollo que rigen para todos los agentes (M0-M6) y la interacción humana en el pipeline.

---

## 1. El Código es un Subproducto de la Especificación
- **Regla de Oro:** Ningún agente de desarrollo (M5) puede escribir código fuente en `app_result/src/` si dicho cambio no está previamente aprobado en `BSP.md` (M2) y ratificado en `ARCHITECTURE.md` (M3).

## 2. Política de Prevención de Desviaciones (Anti-Drift)
- **Definición de Drift:** El drift ocurre cuando el código fuente introduce agentes, herramientas o lógica de negocio que no figuran en las especificaciones.
- **Acciones Ante el Drift:**
  1. Detener la generación de código en M5.
  2. Ejecutar una transición inversa (retroceder el DAG) hacia M2 o M3.
  3. M2/M3 actualizarán los entregables correspondientes.
  4. Retomar la generación en M5 tras la aprobación.

## 3. Registro Estructurado de Decisiones
- Cada entregable de diseño o arquitectura debe contener una sección explícita al final titulada `### Key Decisions`.
- El orquestador leerá este bloque de forma automática y lo anexará al histórico de memoria del proyecto (`MEMORY.md`).

## 4. Cierre de Proyecto y Consolidación de Aprendizajes
- **Gobernanza Post-Proyecto:** Al finalizar el ciclo de desarrollo (con la finalización de M6), es mandatorio actualizar el histórico global de lecciones aprendidas del framework.
- El desarrollador o el agente orquestador debe extraer los aprendizajes técnicos y errores operativos de la bitácora y registrarlos en `.swarm_template/.swarn/memory/development_process_memory.md` (Memoria de Mejora del Swarm) antes de dar por cerrada la rama.
