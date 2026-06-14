import hashlib
import json
import sys
import psycopg2
from typing import Any, Dict, Optional, List
from core.config import settings
from core.providers.embeddings import EmbeddingProvider, GeminiEmbeddingProvider

class MemoryService:
    def __init__(self, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db_url = settings.database_url
        self.node_id = settings.node_id
        self.node_token = settings.node_token
        self.embedding_provider = embedding_provider or GeminiEmbeddingProvider(settings.gemini_api_key)
        self._conn = None

    def _get_connection(self):
        if self._conn is not None:
            try:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                return self._conn
            except Exception:
                self._conn = None

        try:
            self._conn = psycopg2.connect(self.db_url)
            self._conn.autocommit = True
            return self._conn
        except Exception as e:
            print(f"[MemoryService] Connection failed: {e}", file=sys.stderr)
            raise

    def _authenticate(self, cur) -> bool:
        token = self.node_token.split(":", 1)[1] if ":" in self.node_token else self.node_token
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        cur.execute("SELECT token_hash FROM swarm_nodes WHERE node_id = %s;", (self.node_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO swarm_nodes (node_id, token_hash, version) VALUES (%s, %s, %s);", 
                        (self.node_id, token_hash, settings.version))
            return True
        
        if row[0] != token_hash:
            return False
            
        cur.execute("UPDATE swarm_nodes SET version = %s, last_seen = CURRENT_TIMESTAMP WHERE node_id = %s;", 
                    (settings.version, self.node_id))
        return True

    def get_latest_system_version(self) -> str:
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM swarm_nodes WHERE version != 'unknown' ORDER BY version DESC LIMIT 1;")
                row = cur.fetchone()
                return row[0] if row else "0.0.0"
        except Exception:
            return "0.0.0"

    def push_memory(self, project_id: str, phase: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                if not self._authenticate(cur):
                    return False

                metadata = metadata or {}
                metadata.update({"version": settings.version, "node": self.node_id})
                
                cur.execute("""
                    INSERT INTO sga_l0_context (node_id, project_id, phase, content, metadata, env_tier)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (self.node_id, project_id, phase, content, json.dumps(metadata), settings.env_tier))

                embedding = self.embedding_provider.get_embedding(content)
                if embedding:
                    cur.execute("""
                        INSERT INTO sga_l1_swarm_knowledge (node_id, project_id, phase, content, embedding, metadata, env_tier)
                        VALUES (%s, %s, %s, %s, %s::vector, %s, %s);
                    """, (self.node_id, project_id, phase, content, embedding, json.dumps(metadata), settings.env_tier))
            return True
        except Exception as e:
            print(f"[MemoryService] Push error: {e}", file=sys.stderr)
            return False

    def query_memory(self, query: str, limit: int = 5) -> str:
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                if not self._authenticate(cur):
                    return "Auth failed"

                embedding = self.embedding_provider.get_embedding(query)
                if embedding:
                    cur.execute("""
                        SELECT content FROM sga_l1_swarm_knowledge 
                        WHERE env_tier = %s ORDER BY embedding <=> %s::vector LIMIT %s;
                    """, (settings.env_tier, embedding, limit))
                else:
                    cur.execute("""
                        SELECT content FROM sga_l0_context 
                        WHERE env_tier = %s AND content ILIKE %s ORDER BY created_at DESC LIMIT %s;
                    """, (settings.env_tier, f"%{query}%", limit))
                
                rows = cur.fetchall()
                return "\n\n".join([r[0] for row in rows]) if rows else "No memories found."
        except Exception:
            return "Error querying memory."
