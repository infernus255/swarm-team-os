# Swarm Testing Guide & Self-Verification Protocol

Este documento sirve como manual para que los agentes de desarrollo (M5) y control de calidad (M4) ejecuten, validen y depuren pruebas de manera autónoma en este proyecto.

---

## 1. Configuración del Entorno de Pruebas
*Para ser completado por el Arquitecto (M3) o el DevOps (M6) al iniciar el proyecto.*

- **Tecnología de Pruebas:** [Ej. pytest en Python, Jest en Node, xUnit en .NET]
- **Prerrequisitos:** [Ej. Instalar dependencias con `pip install -r requirements.txt` o `npm install`]
- **Comando de Instalación:**
  ```bash
  # comando para preparar dependencias de testing
  ```

---

## 2. Ejecución de Tests Automatizados
El agente M5 o M4 debe ser capaz de ejecutar el suite de pruebas de forma local mediante el comando estático definido aquí.

- **Comando de Ejecución Global:**
  ```bash
  # comando para correr todos los tests (ej: pytest o npm test)
  ```
- **Comando de Ejecución por Módulo:**
  ```bash
  # comando para correr un test específico (ej: pytest tests/test_modulo.py)
  ```

---

## 3. Protocolo de Auto-Corrección ante Fallos (Self-Correction Loop)
Si el comando de ejecución devuelve un código de salida distinto de `0` (Error / Fallo):
1. **Captura del Trace:** Lee y analiza las últimas 50 líneas de salida estándar (`stdout`) y error estándar (`stderr`).
2. **Localización del Código:** Busca los nombres de archivo y números de línea indicados en el trace dentro del directorio `src/`.
3. **Refactorización:** Aplica correcciones al código fuente respetando estrictamente las reglas funcionales de `bsp/BSP.md`.
4. **Re-verificación:** Vuelve a ejecutar el comando de tests. Repite este ciclo hasta lograr un código de salida `0` (tests exitosos).
5. **Reporte:** Documenta brevemente el error y la solución en el entregable de M5 y en las decisiones clave.
