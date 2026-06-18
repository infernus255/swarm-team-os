"""Harness Skill: Observability Dashboard.
Connects to Neon PostgreSQL (SGA) and displays real-time swarm node status, project states, and L1 knowledge.
Requires: DATABASE_URL env var, psycopg2, python-dotenv.
Usage: python harness/scripts/skill_obs_dashboard.py --mode {summary|nodes|projects|knowledge} [--limit N] [--domain {game|harness|swarm|system}]
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Path setup to include core
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'hermes.env'))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))

DB_URL = os.getenv("DATABASE_URL")

def get_conn():
    if not DB_URL:
        print("[WARNING] DATABASE_URL not found in environment. Dashboard requires a database connection.")
        return None
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        print(f"[WARNING] Could not connect to database: {e}")
        return None

def format_ts(ts):
    if not ts: return "N/A"
    return ts.strftime("%Y-%m-%d %H:%M")

def show_nodes(cur):
    print("\n📡 [NODOS DEL SWARM]")
    print("-" * 75)
    print(f"{'ID del Nodo':<25} | {'Versión':<10} | {'Visto por última vez':<20}")
    print("-" * 75)
    cur.execute("SELECT node_id, version, last_seen FROM swarm_nodes ORDER BY last_seen DESC;")
    for nid, ver, ls in cur.fetchall():
        status = "🟢" if (datetime.now(ls.tzinfo) - ls).total_seconds() < 3600 else "🔴"
        print(f"{status} {nid:<23} | {ver:<10} | {format_ts(ls):<20}")

def show_projects(cur, limit=10):
    print("\n📦 [ESTADO DE PROYECTOS (L0)]")
    print("-" * 75)
    print(f"{'ID del Proyecto':<35} | {'Entradas':<8} | {'Última Fase'}")
    print("-" * 75)
    cur.execute("""
        SELECT project_id, COUNT(*), MAX(phase), MAX(created_at)
        FROM sga_l0_context
        GROUP BY project_id
        ORDER BY MAX(created_at) DESC
        LIMIT %s;
    """, (limit,))
    for pid, count, phase, last in cur.fetchall():
        print(f"{pid:<35} | {count:<8} | {phase}")

def show_knowledge(cur, limit=5, domain=None):
    print(f"\n🧠 [CONOCIMIENTO GLOBAL (L1) - {domain if domain else 'ALL'}]")
    print("-" * 75)
    query = "SELECT project_id, content, metadata->>'category', created_at FROM sga_l1_swarm_knowledge "
    if domain:
        query += "WHERE metadata->>'domain' = %s "
    query += "ORDER BY created_at DESC LIMIT %s;"
    
    if domain:
        cur.execute(query, (domain, limit))
    else:
        cur.execute(query, (limit,))

    for pid, content, cat, ts in cur.fetchall():
        snippet = content[:80].replace('\n', ' ')
        print(f"[{format_ts(ts)}] [{pid}] [{cat or 'N/A'}]")
        print(f"   > {snippet}...")

def run_dashboard():
    parser = argparse.ArgumentParser(description="SwarmTeam OS Elite Observability Dashboard")
    parser.add_argument("--mode", choices=["summary", "nodes", "projects", "knowledge"], default="summary")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--domain", choices=["game", "harness", "swarm", "system"])

    args = parser.parse_args()

    print("\n" + "🚀" * 3 + " [SWARMTEAM OS ELITE DASHBOARD v3.1] " + "🚀" * 3)
    
    try:
        conn = get_conn()
        if not conn:
            print("[INFO] Dashboard requires DATABASE_URL. Set it in .env or hermes.env to use this skill.")
            return
        cur = conn.cursor()

        if args.mode == "summary":
            show_nodes(cur)
            show_projects(cur, args.limit)
            show_knowledge(cur, 5, args.domain)
        elif args.mode == "nodes":
            show_nodes(cur)
        elif args.mode == "projects":
            show_projects(cur, args.limit)
        elif args.mode == "knowledge":
            show_knowledge(cur, args.limit, args.domain)

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n" + "="*75)
    print(f"Dashboard generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_dashboard()
