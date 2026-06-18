"""
cleanup_neon_db.py - Realiza la limpieza recomendada en la SGA Neon DB.
1. Renombra 'mobile-game-base-setup' -> 'PROJECT_FORGE_2D_V1.4'
2. Elimina proyectos basura: INTEGRATION_TEST, TEST_PROJECT, new_project
"""
import sys, os
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
    print("\n" + "="*70)
    print("  NEON DB — INICIANDO LIMPIEZA DE LA SGA")
    print("="*70)

    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()

        # 1. Renombrar mobile-game-base-setup -> PROJECT_FORGE_2D_V1.4
        print("\n[1] Renombrando 'mobile-game-base-setup' -> 'PROJECT_FORGE_2D_V1.4'...")
        cur.execute("""
            UPDATE sga_l0_context 
            SET project_id = 'PROJECT_FORGE_2D_V1.4' 
            WHERE project_id = 'mobile-game-base-setup';
        """)
        count0 = cur.rowcount
        cur.execute("""
            UPDATE sga_l1_swarm_knowledge 
            SET project_id = 'PROJECT_FORGE_2D_V1.4' 
            WHERE project_id = 'mobile-game-base-setup';
        """)
        count1 = cur.rowcount
        print(f"    Done: {count0} filas en L0, {count1} filas en L1.")

        # 2. Eliminar proyectos basura
        trash_projects = ('INTEGRATION_TEST', 'TEST_PROJECT', 'new_project')
        print(f"\n[2] Eliminando proyectos basura: {trash_projects}...")
        cur.execute("""
            DELETE FROM sga_l0_context 
            WHERE project_id IN %s;
        """, (trash_projects,))
        count0 = cur.rowcount
        cur.execute("""
            DELETE FROM sga_l1_swarm_knowledge 
            WHERE project_id IN %s;
        """, (trash_projects,))
        count1 = cur.rowcount
        print(f"    Done: {count0} filas eliminadas en L0, {count1} en L1.")

        print("\n✅ LIMPIEZA COMPLETADA CON ÉXITO")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR durante la limpieza: {e}")
        sys.exit(1)

    print("="*70 + "\n")

if __name__ == "__main__":
    run()
