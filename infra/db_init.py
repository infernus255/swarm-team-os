import os
import sys
import hashlib
import psycopg2
import platform
from psycopg2.extras import RealDictCursor
from pathlib import Path

# Parse environment file manually to avoid external dependency issues on host
def load_env_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                # Strip quotes if present
                val = val.strip().strip("'\"")
                os.environ[key.strip()] = val

# Load env variables from hermes.env
load_env_file("hermes.env")

# Fallback to .env in AppData or workspace if present
load_env_file(".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Check if we have the connection string from user prompt as fallback
    DATABASE_URL = "postgresql://neondb_owner:npg_ofE7Ie8gQasT@ep-fancy-thunder-ack1oc7m.sa-east-1.aws.neon.tech/neondb?sslmode=require"
    os.environ["DATABASE_URL"] = DATABASE_URL

NODE_ID = os.getenv("NODE_ID") or platform.node() or "unknown_node"
NODE_TOKEN = os.getenv("NODE_TOKEN", "default_secret_node_token")

# Get Version from file
VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"
CURRENT_VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "unknown"

def clean_token(token: str) -> str:
    if ":" in token:
        # Matches the bash regex sed -E 's/^[a-zA-Z0-9_]+://'
        parts = token.split(":", 1)
        if parts[0].isalnum() or "_" in parts[0]:
            return parts[1]
    return token

def main():
    print(f"Initializing/Migrating Neon Database for SwarmTeam OS on node '{NODE_ID}' (v{CURRENT_VERSION})...")
    
    cleaned_token = clean_token(NODE_TOKEN)
    token_hash = hashlib.sha256(cleaned_token.encode("utf-8")).hexdigest()
    
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        # 1. Enable pgvector extension
        print("Enabling vector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Create/Update swarm_nodes table
        print("Ensuring swarm_nodes table exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS swarm_nodes (
                node_id VARCHAR(100) PRIMARY KEY,
                token_hash VARCHAR(64) NOT NULL,
                registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                version VARCHAR(50) DEFAULT 'unknown'
            );
        """)
        # Add version column if it doesn't exist
        cur.execute("ALTER TABLE swarm_nodes ADD COLUMN IF NOT EXISTS version VARCHAR(50) DEFAULT 'unknown';")
        
        # 3. Create/Update sga_l0_context table (context traces)
        print("Ensuring sga_l0_context table exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sga_l0_context (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(100) REFERENCES swarm_nodes(node_id) ON DELETE CASCADE,
                project_id VARCHAR(100) NOT NULL,
                phase VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                env_tier VARCHAR(20) DEFAULT 'DEV',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Add env_tier column if it doesn't exist
        cur.execute("ALTER TABLE sga_l0_context ADD COLUMN IF NOT EXISTS env_tier VARCHAR(20) DEFAULT 'DEV';")
        
        # 4. Create/Update sga_l1_swarm_knowledge table (vector memories)
        print("Ensuring sga_l1_swarm_knowledge table exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sga_l1_swarm_knowledge (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(100) REFERENCES swarm_nodes(node_id) ON DELETE CASCADE,
                project_id VARCHAR(100) NOT NULL,
                phase VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                embedding vector(768),
                metadata JSONB,
                env_tier VARCHAR(20) DEFAULT 'DEV',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Add env_tier column if it doesn't exist
        cur.execute("ALTER TABLE sga_l1_swarm_knowledge ADD COLUMN IF NOT EXISTS env_tier VARCHAR(20) DEFAULT 'DEV';")
        
        # 5. Create HNSW index for vector queries
        print("Ensuring HNSW vector index exists...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS sga_l1_hnsw_idx 
            ON sga_l1_swarm_knowledge 
            USING hnsw (embedding vector_cosine_ops);
        """)
        
        # 6. Seed/Register current node with version
        print(f"Registering node '{NODE_ID}' with version '{CURRENT_VERSION}'...")
        cur.execute("""
            INSERT INTO swarm_nodes (node_id, token_hash, version)
            VALUES (%s, %s, %s)
            ON CONFLICT (node_id) 
            DO UPDATE SET 
                token_hash = EXCLUDED.token_hash, 
                version = EXCLUDED.version,
                last_seen = CURRENT_TIMESTAMP;
        """, (NODE_ID, token_hash, CURRENT_VERSION))
        
        print("Database initialization and migration completed successfully!")
    except Exception as e:
        print(f"Migration error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
