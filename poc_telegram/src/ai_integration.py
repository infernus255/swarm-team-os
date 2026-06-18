import openai
import json

class AIProcessor:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    async def transcribe_audio(self, audio_path):
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text

    async def extract_price_data(self, text):
        # Strict Prompting for Zero Tolerance to Error
        system_prompt = """
        You are a highly precise retail assistant. Extract price updates from the user's text.
        Output MUST be a JSON object with keys: "product" (string), "price" (float), "action" (one of: 'up', 'down', 'fixed').
        If the input is ambiguous, incomplete, or lacks critical information, return an error object: {"error": "ambiguous"}.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception:
            return json.dumps({"error": "processing_failed"})
