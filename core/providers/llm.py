import os
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
        """Classifies a task to select the optimal engine."""
        system_prompt = """
        Eres el Clasificador Inteligente de SwarmTeam OS. 
        Tu tarea es analizar el requerimiento del usuario y determinar qué 'engine' de swarm es el más adecuado.
        
        Engines disponibles:
        1. '.swarm_antigravity_sdk': Para tareas que involucren el SDK de Google Antigravity, orquestación compleja de agentes de Google, o si se menciona explícitamente 'antigravity'.
        2. '.swarm_pydantic_fast': Para aplicaciones web (FastAPI), validación de datos (Pydantic), o si se busca una estructura de tipos rigurosa con PydanticAI.
        3. '.swarm_copilot': Para generar instrucciones de VS Code Copilot, archivos .github/copilot-instructions.md o prompts para IDEs.
        4. '.swarm_template': Solo si es un requerimiento muy genérico que no encaja en los anteriores.

        Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
        {
          "selected_engine": ".folder_name",
          "reason": "breve explicación de la elección",
          "complexity": "low|medium|high"
        }
        """
        
        result = await self.generate_text(prompt, system_instruction=system_prompt)
        
        try:
            # Clean possible markdown junk
            json_str = result.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3].strip()
            elif json_str.startswith("```"):
                json_str = json_str[3:-3].strip()
            
            return json.loads(json_str)
        except Exception:
            return {
                "selected_engine": ".swarm_antigravity_sdk",
                "reason": f"Fallback due to classification error. Raw output: {result}",
                "complexity": "medium"
            }

llm_provider = LLMProvider()
