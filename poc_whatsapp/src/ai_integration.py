
import openai

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
        # Using Structured Outputs (JSON)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract: product, price, action (up/down/fixed). Return JSON."},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
