from abc import ABC, abstractmethod
from typing import List, Optional

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> Optional[List[float]]:
        pass

class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str):
        self.api_key = self._clean_key(api_key)
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"

    def _clean_key(self, key: str) -> str:
        return key.split(":", 1)[1] if key and ":" in key else key

    def get_embedding(self, text: str) -> Optional[List[float]]:
        import requests
        if not self.api_key:
            return None
        
        payload = {
            "model": "models/gemini-embedding-2",
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": 768
        }
        try:
            response = requests.post(f"{self.url}?key={self.api_key}", json=payload, timeout=5)
            if response.status_code == 200:
                return response.json()["embedding"]["values"]
        except Exception:
            pass
        return None
