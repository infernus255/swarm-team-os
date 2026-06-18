import os
import json
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from core.config import settings

class LLMProvider:
    """Unified LLM provider for SwarmTeam OS Core."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.default_model = model_name or settings.model_tier1

    async def generate_text(self, prompt: str, model_name: Optional[str] = None, system_instruction: Optional[str] = None) -> str:
        """Generates text using the specified model."""
        if not self.client:
            return "ERROR: No API Key configured for Gemini."

        target_model = model_name or self.default_model
        
        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            return response.text
        except Exception as e:
            return f"ERROR calling LLM: {str(e)}"

    async def classify_task(self, prompt: str) -> Dict[str, Any]:
        """Classifies a task to select the optimal engine with high precision."""
        system_prompt = """
        Eres el Clasificador Inteligente de SwarmTeam OS Elite v3.1. 
        Tu tarea es realizar una auditoría técnica del requerimiento del usuario para delegarlo al motor (engine) más eficiente.
        
        CATÁLOGO DE ENGINES:
        1. '.swarm_antigravity_sdk': 
           - Casos de uso: Orquestación multi-agente, uso del SDK de Google Antigravity, lógica de grafos de agentes compleja.
           - Palabras clave: agents, swarm orchestration, autonomy, antigravity.
        2. '.swarm_pydantic_fast': 
           - Casos de uso: APIs backend, validación de esquemas Pydantic, PydanticAI, microservicios rápidos.
           - Palabras clave: fastapi, pydantic, schema, web service, rest api.
        3. '.swarm_copilot': 
           - Casos de uso: Configuración de entornos de desarrollo, instrucciones para VS Code, estandarización de prompts de IDE.
           - Palabras clave: copilot, .github, instructions, developer experience.
        4. '.swarm_template': 
           - Casos de uso: Solo para prototipos genéricos o investigación inicial de archivos.

        REGLAS DE SALIDA:
        - Debes responder EXCLUSIVAMENTE con un objeto JSON válido.
        - No incluyas explicaciones fuera del JSON.
        - Si el requerimiento es ambiguo, selecciona '.swarm_antigravity_sdk' como predeterminado.

        FORMATO JSON REQUERIDO:
        {
          "selected_engine": ".folder_name",
          "reason": "Explicación técnica de la arquitectura seleccionada",
          "complexity": "low|medium|high",
          "detected_tech_stack": ["lista", "de", "tecnologías", "detectadas"]
        }
        """
        
        result = await self.generate_text(prompt, system_instruction=system_prompt)
        
        try:
            # Clean possible markdown junk or additional text
            json_str = result.strip()
            if "{" in json_str and "}" in json_str:
                json_str = json_str[json_str.find("{"):json_str.rfind("}")+1]
            
            data = json.loads(json_str)
            # Ensure mandatory fields
            if "selected_engine" not in data:
                raise ValueError("Missing 'selected_engine' in LLM response")
            return data
        except Exception as e:
            print(f"⚠️ [LLMProvider]: Classification parsing failed: {e}. Raw output: {result}")
            return {
                "selected_engine": ".swarm_antigravity_sdk",
                "reason": "Fallback: Error parsing LLM classification response.",
                "complexity": "medium",
                "detected_tech_stack": []
            }

llm_provider = LLMProvider()
