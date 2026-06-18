"""
sync_lore_db.py - Sube TODO el aprendizaje del proyecto a la SGA Neon DB

Cubre:
  - Aprendizajes de gameplay / producto (Project Forge 2D)
  - Insights de ingeniería agnosticos (Harness, Swarm, Core)
  - Lecciones del diff develop → feat/mobile-game
  - Patrones de testing, observabilidad y E2E
  - Anti-patrones y regresiones encontradas

Diseñado para ser 100% agnostico al proyecto: los insights del harness
se guardan con project_id="HARNESS_AGNOSTIC" para que cualquier nodo
del swarm los pueda recuperar.
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.sga_client import sga_client

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def push(project_id, phase, content, category, tags, domain):
    ok = sga_client.push_memory(
        project_id=project_id,
        phase=phase,
        content=content,
        metadata={"category": category, "tags": tags, "domain": domain}
    )
    status = "✅" if ok else "❌"
    print(f"  {status}  [{category}] {content[:80]}...")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# 1. GAMEPLAY / PRODUCT — Project Forge 2D (PES 1.4)
# ─────────────────────────────────────────────────────────────────────────────

GAME_PROJECT = "PROJECT_FORGE_2D_V1.4"
GAME_PHASE   = "GAMEPLAY_ROADMAP_COMPLETE"
GAME_DOMAIN  = "game"

GAME_MEMORIES = [
    (
        "Celular automata physics en JS con TypedArrays planos (Uint8Array, Uint32Array) es la clave "
        "para 60 FPS en móvil sin WebGL. El patrón clock-bit (1 byte por celda que alterna cada frame) "
        "evita dobles actualizaciones en el mismo paso físico, lo que hace el motor determinístico. "
        "Nunca usar new Array() dentro del loop de simulación — solo TypedArrays de tamaño fijo.",
        "physics_engine", ["cellular_automata", "typescript_arrays", "performance", "determinism"]
    ),
    (
        "El bug de 'sinking' (entidades hundiéndose en el suelo) ocurre cuando coordenadas float "
        "se redondean mal al comparar con la grilla de enteros del CA. Solución: agregar unstuck() "
        "al inicio de cada update() que escanea 24px hacia arriba y mueve la entidad al primer "
        "espacio libre. Reemplazar divisiones con Math.floor() con loops pixel-a-pixel para snap exacto.",
        "physics_fixes", ["sinking_bug", "collision", "unstuck", "float_rounding"]
    ),
    (
        "Los proyectiles elementales del báculo deben mapear el material seleccionado en la paleta "
        "al tipo de proyectil: MAT.FIRE→fire (explota radio 6), MAT.ACID→acid (disuelve bloques radio 4), "
        "MAT.ICE→ice (congela agua/oil, aplica slowTimer=180 a enemigos), MAT.LAVA→plasma (25 dmg, "
        "funde STONE→LAVA). Cada tipo tiene visual distinto con shadowBlur y color único.",
        "game_mechanics", ["elemental_shots", "staff", "projectiles", "materials"]
    ),
    (
        "El Cyber-Dash (Spacebar) requiere: dashTimer=12 frames de duración, dashCooldown=35 frames, "
        "iframes con dmgTimer=max(dmgTimer,2), trail de partículas CA (EMBER+SMOKE) en posición behind, "
        "y ghost silhouettes translúcidas cian dibujadas durante el dash. El facing debe bloquearse "
        "mientras dashTimer > 0 para que la velocidad no cambie de dirección.",
        "game_mechanics", ["dash", "dodge_roll", "iframes", "visual_feedback"]
    ),
    (
        "Las reliquias de historia (Ankh de Vida, Ojo de Horus, Escarabajo de Poder) deben activar "
        "efectos pasivos en Player.update() — no en el momento de recolección. Ankh: +1HP cada 60 frames "
        "con ankhRegenTimer, reducción 25% de daño de peligros. Eye: línea dashed cian desde player "
        "al cofre más cercano con world-wrapping (shortest-path). Scarab: slider.max='12' en DOM, "
        "mineCooldown reducido de 8 a 4 frames.",
        "game_mechanics", ["relics", "passive_perks", "story_mode", "hud"]
    ),
    (
        "WebRTC P2P invite links: al copiar el código de host, generar URL completa "
        "window.location.origin + pathname + '#join=' + code. Al cargar la página, parsear "
        "window.location.hash con startsWith('#join=') y llamar mp.join(offer) automáticamente. "
        "Esto elimina la fricción de pegar código manualmente para el invitado.",
        "multiplayer", ["webrtc", "invite_links", "p2p", "ux"]
    ),
    (
        "El Pharaoh Guardian (boss, 400 HP) tiene dos fases: Fase 1 (HP>=50%) dispara proyectiles "
        "boss_energy guiados cada 55 frames. Fase 2 (HP<50%/furia) dispara cada 35 frames, invoca "
        "murciélagos y activa halo rojo. Al morir: shake pantalla, explosión de partículas, suelta "
        "ankh_of_ra que activa triggerVictory(). El campo de fuerza en x=[445,575] y>=250 rechaza "
        "al jugador si no tiene las 3 reliquias en modo survival.",
        "boss_design", ["pharaoh_guardian", "boss_phases", "force_field", "victory_condition"]
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. INGENIERÍA AGNOSTICA — Harness, Swarm, Core (aplica a cualquier proyecto)
# ─────────────────────────────────────────────────────────────────────────────

HARNESS_PROJECT = "HARNESS_AGNOSTIC"
HARNESS_PHASE   = "SWARM_LEARNINGS_FROM_FORGE2D"
HARNESS_DOMAIN  = "harness"

HARNESS_MEMORIES = [
    (
        "HARNESS PATTERN — E2E Testing con Playwright sin framework: crear scripts Node.js "
        "standalone (play_game_e2e.js) que lanzan un http-server local, abren Chromium headless "
        "con playwright/chromium, inyectan inputs via page.keyboard.down(), y leen estado del juego "
        "via page.evaluate(). Esto valida comportamiento real sin mocks. El script debe auto-cerrar "
        "el servidor y el browser en cualquier exit path.",
        "testing_pattern", ["e2e", "playwright", "headless", "validation"]
    ),
    (
        "HARNESS PATTERN — El harness debe ser 100% agnóstico al producto. skill_state.py, "
        "skill_plan.py, skill_guru_watch.py no deben importar ni referenciar ningún modelo de "
        "dominio del producto (Game, Player, etc). El único contrato es: el harness recibe "
        "un directorio de repo + config de entorno y produce telemetría, planes y sincs a Neon. "
        "Los tests de repo_validation deben validar rutas de scripts, no lógica de producto.",
        "architecture", ["agnostic", "harness", "separation_of_concerns", "dependency_inversion"]
    ),
    (
        "HARNESS PATTERN — skill_state.py en el diff develop→feat/mobile-game creció de 35 a 377 "
        "líneas. El crecimiento fue: agregar hash de API keys (SHA256 truncado a 16 chars para "
        "mostrar sin exponer), parseo de api_key_limits.json con fallback a env var API_KEY_LIMITS, "
        "y soporte multi-key con aliases (formato 'alias:key'). Lección: el sistema de API keys "
        "del harness debe ser agnóstico al proveedor — funciona con GEMINI, OPENAI, ANTHROPIC, etc.",
        "api_key_management", ["multi_key", "aliasing", "rate_limits", "security"]
    ),
    (
        "HARNESS PATTERN — state.lock eliminado del repo en este branch. Los archivos de lock de "
        "estado dinámico (state.lock, state.json) no deben estar en git — son artefactos runtime "
        "que cambian en cada ejecución del nodo. Deben estar en .gitignore. Solo state.json "
        "con snapshot de telemetría puede ser útil para debugging, pero nunca en producción.",
        "git_hygiene", ["state_files", "gitignore", "runtime_artifacts"]
    ),
    (
        "SWARM PATTERN — La MemoryService (core/services/memory_service.py) usa dos capas: "
        "L0 (sga_l0_context) para contexto de proyecto específico, L1 (sga_l1_swarm_knowledge) "
        "para conocimiento global con embeddings vectoriales. Al hacer push_memory(), siempre "
        "intentar generar embedding con GeminiEmbeddingProvider — si falla, el L0 sigue funcionando "
        "como fallback sin vector. La autenticación usa SHA256 del node_token para evitar exponer "
        "tokens en texto plano en la DB.",
        "memory_architecture", ["sga", "l0_l1", "embeddings", "vector_search", "authentication"]
    ),
    (
        "SWARM PATTERN — En el diff develop→feat/mobile-game, jarvis.py recibió integración con "
        "Neon DB para subir lore a sga_l0_context en cada run exitoso. El patrón correcto es: "
        "ejecutar la tarea principal primero, y solo al final (en caso de éxito) sincronizar "
        "aprendizajes a la DB. Nunca bloquear la ejecución principal esperando confirmación de DB.",
        "orchestration", ["jarvis", "neon_db", "async_sync", "error_handling"]
    ),
    (
        "TESTING PATTERN — Los tests de repo_validation deben usar pathlib.Path para ser "
        "cross-platform (Windows/Linux/macOS). Evitar os.path.join() con strings hardcodeadas. "
        "Los paths de scripts del harness deben ser relativos a REPO_ROOT, no absolutos. "
        "Esto permite que el mismo test funcione en Docker, Windows bare-metal y CI/CD.",
        "testing_pattern", ["cross_platform", "pathlib", "repo_validation", "portability"]
    ),
    (
        "ARCHITECTURE PATTERN — El EngineSelector (core/engine_selector.py) debe usar "
        "clasificación por keywords como Tier 0 (rápido, sin costo) antes de invocar a Gemini Flash "
        "para clasificación inteligente. El crecimiento de 0 a 10898 bytes en este diff indica que "
        "se agregó la lógica de enrutamiento dinámico. Patrón: keywords → regex → LLM classifier, "
        "cada nivel más costoso pero más preciso.",
        "engine_routing", ["engine_selector", "classification", "tiered_routing", "cost_optimization"]
    ),
    (
        "DEPLOYMENT PATTERN — Para proyectos de frontend puro (HTML+CSS+JS sin bundler), "
        "vercel.json con builds usando @vercel/static es suficiente. Listar explícitamente cada "
        "archivo estático (index.html, css/*.css, js/*.js) en lugar de usar wildcards para tener "
        "control total sobre qué se expone. npx vercel --prod --yes permite deploy no-interactivo "
        "para integración en pipelines automáticos.",
        "deployment", ["vercel", "static_hosting", "ci_cd", "non_interactive"]
    ),
    (
        "PERFORMANCE PATTERN — Canvas 2D con putImageData() sobre un offscreen canvas es "
        "10-20x más rápido que drawRect() por celda. El patrón correcto: tener un Uint32Array "
        "de colores (ABGR format), modificarlo en el loop de física, y hacer un solo putImageData() "
        "al final de cada frame. Nunca llamar a ctx.fillRect() dentro del loop de CA.",
        "performance", ["canvas_2d", "putImagedata", "offscreen_canvas", "render_optimization"]
    ),
    (
        "OBSERVABILITY PATTERN — El panel debug en juego debe mostrar en tiempo real: posición "
        "exacta (x,y), velocidad (vx,vy), cámara (cam.x, cam.y), estado de reliquias, proximidad "
        "al campo de fuerza, y count de enemigos activos. Activado desde settings panel con un toggle. "
        "Este mismo patrón aplica a cualquier sistema de agentes: exponer estado interno vía endpoint "
        "debug sin impactar el flujo principal.",
        "observability", ["debug_panel", "state_visibility", "runtime_metrics", "agnostic"]
    ),
    (
        "WASM SCAFFOLD PATTERN — Al preparar migración a WebAssembly (Roadmap V2): "
        "(1) Crear directorio wasm_engine/ con Cargo.toml (crate-type=['cdylib','rlib']), "
        "(2) src/lib.rs con #[wasm_bindgen] exports de funciones públicas, "
        "(3) Script de build con wasm-pack build --target web --release, "
        "(4) Profile release con opt-level='s' + lto=true para minimizar tamaño binario. "
        "El scaffold permite que el equipo valide la API antes de tener Rust instalado.",
        "wasm_migration", ["rust", "wasm_bindgen", "wasm_pack", "scaffold", "migration_pattern"]
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. DIFF INSIGHTS — develop → feat/mobile-game
# ─────────────────────────────────────────────────────────────────────────────

DIFF_PROJECT = "SWARM_DIFF_ANALYSIS"
DIFF_PHASE   = "DEVELOP_VS_MOBILE_GAME_2026_06_17"
DIFF_DOMAIN  = "harness"

DIFF_MEMORIES = [
    (
        "DIFF ANALYSIS — develop→feat/mobile-game: 239 archivos cambiados, +360k líneas. "
        "El volumen principal es node_modules/ (Playwright) que NO debería estar en el diff "
        "— confirma que node_modules/ estuvo fuera del .gitignore en develop. "
        "ACCIÓN: agregar node_modules/ al .gitignore en develop también.",
        "diff_analysis", ["node_modules", "gitignore_gap", "diff_noise"]
    ),
    (
        "DIFF ANALYSIS — Archivos de juego nuevos en feat/mobile-game vs develop: "
        "index.html (+9469B), css/style.css (nuevo), js/physics.js (+18325B), js/audio.js (+6272B), "
        "js/game.js (+105429B), js/multiplayer.js (+4260B), js/main.js (+906B), vercel.json (+525B). "
        "Total de juego: ~145KB de código original. El juego se construyó desde cero en esta rama.",
        "diff_analysis", ["game_files", "branch_delta", "new_features"]
    ),
    (
        "DIFF ANALYSIS — harness/scripts/skill_state.py: 35→377 líneas (+342). "
        "Cambios: reemplazó TelemetryOrchestrator (acoplado a GitCollector/SystemCollector) "
        "por funciones puras con StateLoader. Agregó: hash de API keys, parseo multi-key, "
        "soporte api_key_limits.json, encoding UTF-8 fix para Windows. "
        "LECCIÓN: el harness se volvió más robusto al eliminar clases de estado y usar funciones puras.",
        "harness_evolution", ["skill_state", "refactoring", "pure_functions", "windows_compat"]
    ),
    (
        "DIFF ANALYSIS — harness/scripts/skill_plan.py: solo cambió REPO_ROOT de parents[1] a "
        "parents[2]. Esto indica que la ubicación relativa del script cambió (movido un nivel más "
        "profundo en la jerarquía de directorios). PATRÓN: siempre usar StateLoader o una "
        "constante REPO_ROOT calculada desde __file__ para evitar paths frágiles.",
        "harness_evolution", ["repo_root", "path_fragility", "skill_plan"]
    ),
    (
        "DIFF ANALYSIS — tests/test_sga_client.py: solo 2 líneas cambiadas (de la comparación develop). "
        "tests/test_repo_validation.py: 4 tests nuevos que validan rutas de scripts del harness. "
        "PATRÓN: los tests de validación del repo son los primeros en romperse cuando se mueven "
        "archivos sin actualizar las referencias. Son el 'smoke test' del harness.",
        "testing_pattern", ["smoke_tests", "repo_validation", "path_tests", "fragility_detection"]
    ),
    (
        "DIFF ANALYSIS — scratch/ directorio nuevo: 7 archivos (5 E2E scripts + playwright_benchmark.js "
        "+ sync_lore_db.py). El patrón es correcto: scripts de validación y utilidades en scratch/ "
        "separados del código de producción. Estos no se importan desde ningún módulo, son "
        "ejecutables standalone. La misma carpeta puede usarse para cualquier proyecto del swarm.",
        "project_structure", ["scratch_dir", "e2e_scripts", "standalone_scripts", "swarm_pattern"]
    ),
    (
        "DIFF ANALYSIS — wasm_engine/ nuevo en feat/mobile-game: Cargo.toml + src/lib.rs + build_wasm.ps1. "
        "Este directorio es el scaffold del Roadmap V2 (WASM). Como develop no tiene Rust instalado "
        "y el código Rust no está en el critical path del juego actual, se puede mantener en el repo "
        "sin que bloquee a developers que no tienen Rust. El .gitignore excluye target/ y wasm_pkg/.",
        "wasm_migration", ["wasm_engine", "scaffold", "non_blocking", "roadmap_v2"]
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"  SGA Neon DB Sync — {timestamp}")
    print(f"{'='*60}\n")

    results = []

    print(f"📦 BLOQUE 1: Gameplay / Product (project={GAME_PROJECT})")
    for content, category, tags in GAME_MEMORIES:
        ok = push(GAME_PROJECT, GAME_PHASE, content, category, tags, GAME_DOMAIN)
        results.append(ok)

    print(f"\n🔧 BLOQUE 2: Ingeniería Agnóstica — Harness & Swarm (project={HARNESS_PROJECT})")
    for content, category, tags in HARNESS_MEMORIES:
        ok = push(HARNESS_PROJECT, HARNESS_PHASE, content, category, tags, HARNESS_DOMAIN)
        results.append(ok)

    print(f"\n🔍 BLOQUE 3: Diff Insights develop→feat/mobile-game (project={DIFF_PROJECT})")
    for content, category, tags in DIFF_MEMORIES:
        ok = push(DIFF_PROJECT, DIFF_PHASE, content, category, tags, DIFF_DOMAIN)
        results.append(ok)

    total = len(results)
    success = sum(results)
    failed  = total - success

    print(f"\n{'='*60}")
    print(f"  SYNC COMPLETE: {success}/{total} memorias subidas ✅ | {failed} fallidas ❌")
    print(f"{'='*60}\n")

    if failed > 0:
        print("⚠️  Algunas memorias no se sincronizaron. Verificar DATABASE_URL y GEMINI_API_KEY en hermes.env")
        sys.exit(1)


if __name__ == "__main__":
    main()
