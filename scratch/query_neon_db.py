"""
query_neon_db.py - Consulta y muestra todo el contenido de la SGA Neon DB
Muestra: nodos registrados, memorias L0 por proyecto, counts por categoria.
Identifica si hay mezcla entre lore de juego y conocimiento del swarm.
"""
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hermes.env'))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

import psycopg2

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("ERROR: DATABASE_URL no encontrada en .env / hermes.env")
    sys.exit(1)

def run():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("\n" + "="*70)
    print("  NEON DB — ESTADO COMPLETO DE LA SGA")
    print("="*70)

    # ── 1. Nodos registrados ─────────────────────────────────────────────────
    print("\n[1] NODOS REGISTRADOS (swarm_nodes)")
    print("-"*50)
    try:
        cur.execute("SELECT node_id, version, last_seen FROM swarm_nodes ORDER BY last_seen DESC;")
        rows = cur.fetchall()
        if not rows:
            print("  (ninguno)")
        for node_id, version, last_seen in rows:
            print(f"  node={node_id}  v={version}  last_seen={last_seen}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 2. Resumen por project_id en L0 ─────────────────────────────────────
    print("\n[2] MEMORIAS L0 — por project_id")
    print("-"*50)
    try:
        cur.execute("""
            SELECT project_id, COUNT(*) as total,
                   MIN(created_at)::date as desde,
                   MAX(created_at)::date as hasta
            FROM sga_l0_context
            GROUP BY project_id
            ORDER BY total DESC;
        """)
        rows = cur.fetchall()
        if not rows:
            print("  (tabla vacía)")
        for pid, total, desde, hasta in rows:
            print(f"  {pid:<40} {total:>4} memorias  ({desde} → {hasta})")
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 3. Memorias L1 (con embeddings) ─────────────────────────────────────
    print("\n[3] MEMORIAS L1 (con vector embedding) — por project_id")
    print("-"*50)
    try:
        cur.execute("""
            SELECT project_id, COUNT(*) as total
            FROM sga_l1_swarm_knowledge
            GROUP BY project_id
            ORDER BY total DESC;
        """)
        rows = cur.fetchall()
        if not rows:
            print("  (tabla vacía)")
        for pid, total in rows:
            print(f"  {pid:<40} {total:>4} vectores")
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 4. Desglose por categoría (metadata->>'category') ───────────────────
    print("\n[4] DESGLOSE POR CATEGORIA (L0)")
    print("-"*50)
    try:
        cur.execute("""
            SELECT
                project_id,
                metadata->>'category' as category,
                COUNT(*) as n
            FROM sga_l0_context
            GROUP BY project_id, category
            ORDER BY project_id, n DESC;
        """)
        rows = cur.fetchall()
        if not rows:
            print("  (sin datos)")
        current_proj = None
        for pid, cat, n in rows:
            if pid != current_proj:
                print(f"\n  [{pid}]")
                current_proj = pid
            print(f"    {cat or '(sin categoria)':<35}  {n:>3} entradas")
    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 5. Ultimas 5 memorias por cada project_id (extracto) ────────────────
    print("\n[5] EXTRACTO DE CONTENIDO — ultimas 5 entradas por proyecto")
    print("-"*50)
    try:
        cur.execute("SELECT DISTINCT project_id FROM sga_l0_context ORDER BY project_id;")
        projects = [r[0] for r in cur.fetchall()]
        for pid in projects:
            print(f"\n  ▶ {pid}")
            cur.execute("""
                SELECT content, metadata->>'category', created_at
                FROM sga_l0_context
                WHERE project_id = %s
                ORDER BY created_at DESC
                LIMIT 5;
            """, (pid,))
            for content, cat, ts in cur.fetchall():
                snippet = content[:120].replace('\n', ' ')
                print(f"    [{cat}] {snippet}...")

    except Exception as e:
        print(f"  ERROR: {e}")

    # ── 6. DIAGNÓSTICO: ¿hay mezcla? ────────────────────────────────────────
    print("\n" + "="*70)
    print("  DIAGNOSTICO DE SEPARACION DE CONTEXTOS")
    print("="*70)
    try:
        # Buscar si lore de juego aparece en proyectos del swarm
        cur.execute("""
            SELECT project_id, COUNT(*) as n
            FROM sga_l0_context
            WHERE (
                content ILIKE '%Pharaoh%' OR
                content ILIKE '%Ankh%' OR
                content ILIKE '%cellular automata%' OR
                content ILIKE '%Kemet%' OR
                content ILIKE '%Forge 2D%'
            )
            GROUP BY project_id;
        """)
        game_in_swarm = cur.fetchall()

        # Buscar si lore del swarm aparece en proyectos de juego
        cur.execute("""
            SELECT project_id, COUNT(*) as n
            FROM sga_l0_context
            WHERE (
                content ILIKE '%EngineSelector%' OR
                content ILIKE '%GraphRunner%' OR
                content ILIKE '%sga_client%' OR
                content ILIKE '%Neon DB%' OR
                content ILIKE '%swarm_nodes%'
            )
            GROUP BY project_id;
        """)
        swarm_in_game = cur.fetchall()

        print("\n  Contenido de juego (Pharaoh/Ankh/CA/Kemet/Forge2D) por proyecto:")
        if not game_in_swarm:
            print("    (ninguno en DB aun)")
        for pid, n in game_in_swarm:
            tag = "⚠️  MEZCLA POTENCIAL" if "HARNESS" in pid or "SWARM" in pid else "✅ Correcto"
            print(f"    {pid:<40} {n} entradas  {tag}")

        print("\n  Contenido de swarm (EngineSelector/SGA/etc) por proyecto:")
        if not swarm_in_game:
            print("    (ninguno en DB aun)")
        for pid, n in swarm_in_game:
            tag = "⚠️  MEZCLA POTENCIAL" if "FORGE" in pid or "GAME" in pid else "✅ Correcto"
            print(f"    {pid:<40} {n} entradas  {tag}")

    except Exception as e:
        print(f"  ERROR en diagnóstico: {e}")

    print("\n" + "="*70)
    cur.close()
    conn.close()

if __name__ == "__main__":
    run()
