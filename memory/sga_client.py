import os
import sys
import hashlib
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, Optional, List

# Helper to load environment files
def load_env_file(filepath):
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip("'\"")
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = val
    except Exception as e:
        print(f"[SGA Warning] Could not load env file {filepath}: {e}")

# Load environment configs
load_env_file("hermes.env")
load_env_file("/root/.hermes/.env")
load_env_file(".env")

class SGAClient:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        # Fallback to the known connection string if not found
        if not self.db_url:
            self.db_url = "postgresql://neondb_owner:npg_ofE7Ie8gQasT@ep-fancy-thunder-ack1oc7m.sa-east-1.aws.neon.tech/neondb?sslmode=require"
            
        self.node_id = os.getenv("NODE_ID", "ryzen_muscle")
        self.node_token = os.getenv("NODE_TOKEN", "default_secret_node_token")
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._conn = None

    def _clean_token(self, token: str) -> str:
        if ":" in token:
            parts = token.split(":", 1)
            if parts[0].isalnum() or "_" in parts[0]:
                return parts[1]
        return token

    def _clean_api_key(self, api_key: str) -> str:
        if api_key and ":" in api_key:
            parts = api_key.split(":", 1)
            if parts[0].isalnum() or "_" in parts[0]:
                return parts[1]
        return api_key

    def _get_connection(self):
        """Returns the active cached psycopg2 connection or creates a new one if closed."""
        if self._conn is not None:
            try:
                # Test connection is still alive
                with self._conn.cursor() as test_cur:
                    test_cur.execute("SELECT 1;")
                return self._conn
            except Exception:
                # Connection is dead, clean up and reconnect
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None
        
        try:
            self._conn = psycopg2.connect(self.db_url)
            self._conn.autocommit = True
            return self._conn
        except Exception as e:
            print(f"[SGA] Database connection failed: {e}", file=sys.stderr)
            raise

    def _authenticate(self, cur) -> bool:
        """Verifies that the node_id and node_token match the database registry."""
        cleaned_token = self._clean_token(self.node_token)
        token_hash = hashlib.sha256(cleaned_token.encode("utf-8")).hexdigest()
        
        cur.execute("SELECT token_hash FROM swarm_nodes WHERE node_id = %s;", (self.node_id,))
        row = cur.fetchone()
        if not row:
            # Auto-register node if it's missing (e.g. dynamic node joining)
            print(f"[SGA] Node '{self.node_id}' not registered. Registering...")
            cur.execute("""
                INSERT INTO swarm_nodes (node_id, token_hash)
                VALUES (%s, %s);
            """, (self.node_id, token_hash))
            return True
        else:
            stored_hash = row[0]
            if stored_hash != token_hash:
                print(f"[SGA] Auth Error: Token hash mismatch for node '{self.node_id}'.")
                return False
            return True




    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Retrieves text embedding using Gemini's gemini-embedding-2 model."""
        clean_key = self._clean_api_key(self.api_key)
        if not clean_key:
            print("[SGA] Warning: No GEMINI_API_KEY found, skipping vector embedding generation.")
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={clean_key}"
        payload = {
            "model": "models/gemini-embedding-2",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": 768
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data["embedding"]["values"]
            else:
                print(f"[SGA] Embedding API returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[SGA] Error calling embedding API: {e}")
        return None


    def push_memory(self, project_id: str, phase: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Pushes a memory entry (decision or summary) directly to the Neon PostgreSQL database."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Authenticate Node
            if not self._authenticate(cur):
                cur.close()
                return False

            # Insert into sga_l0_context (Structured history log)
            metadata_json = json.dumps(metadata or {})
            cur.execute("""
                INSERT INTO sga_l0_context (node_id, project_id, phase, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (self.node_id, project_id, phase, content, metadata_json))
            
            l0_id = cur.fetchone()[0]
            print(f"[SGA] Memory persisted in L0 Context (ID: {l0_id})")

            # Try to generate vector embedding for L1 Swarm Knowledge (Vector memory)
            embedding = self._get_embedding(content)
            if embedding:
                # Format embedding as pgvector compatible string format '[v1, v2, ...]'
                embedding_str = "[" + ",".join(map(str, embedding)) + "]"
                cur.execute("""
                    INSERT INTO sga_l1_swarm_knowledge (node_id, project_id, phase, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s::vector, %s)
                    RETURNING id;
                """, (self.node_id, project_id, phase, content, embedding_str, metadata_json))
                l1_id = cur.fetchone()[0]
                print(f"[SGA] Memory persisted in L1 Swarm Knowledge (ID: {l1_id})")
            
            cur.close()
            return True
        except Exception as e:
            print(f"[SGA] Error pushing memory: {e}", file=sys.stderr)
            return False

    def query_global_memory(self, query: str, limit: int = 5) -> str:
        """Queries the database for matching memories, using HNSW vector search with fallback to keyword search."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Authenticate Node
            if not self._authenticate(cur):
                cur.close()
                return "Authentication failed."

            embedding = self._get_embedding(query)
            memories = []

            if embedding:
                # Perform HNSW Cosine Distance search on L1 Swarm Knowledge
                embedding_str = "[" + ",".join(map(str, embedding)) + "]"
                cur.execute("""
                    SELECT content 
                    FROM sga_l1_swarm_knowledge
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """, (embedding_str, limit))
                rows = cur.fetchall()
                memories = [row[0] for row in rows]
                print(f"[SGA] Vector search returned {len(memories)} results.")
            
            # Fallback to ILIKE keyword search on L0 Context if no vector results or embedding failed
            if not memories:
                print("[SGA] Running keyword search fallback...")
                search_pattern = f"%{query}%"
                cur.execute("""
                    SELECT content 
                    FROM sga_l0_context
                    WHERE content ILIKE %s OR project_id ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                """, (search_pattern, search_pattern, limit))
                rows = cur.fetchall()
                memories = [row[0] for row in rows]
                print(f"[SGA] Keyword fallback returned {len(memories)} results.")

            cur.close()
            if not memories:
                return "No global memory context available."
            return "\n\n".join(memories)

        except Exception as e:
            print(f"[SGA] Error querying memory: {e}", file=sys.stderr)
            return "No global memory context available."


sga_client = SGAClient()
