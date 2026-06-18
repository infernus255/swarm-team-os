# WhatsApp Price Assistant PoC

This project is a Proof of Concept for a Voice Price Assistant for WhatsApp.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key.
- `VERIFY_TOKEN`: A token for verifying WhatsApp webhook requests.
- `GOOGLE_CREDENTIALS_FILE`: Path to your Google Service Account JSON key file.
- `SHEET_NAME`: The name of your Google Sheet.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your environment variables in a `.env` file (or provide them directly).
3. Run the application:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 9119
   ```

## WhatsApp Integration

- The application listens for incoming messages on the `/webhook` endpoint.
- It handles audio messages by transcribing them using OpenAI Whisper and extracting product/price information using GPT-4o-mini.
- For interactive confirmation, it currently simulates sending a message with 'YES/NO' buttons. You would need to integrate with the WhatsApp Business API to send these buttons and handle replies.
- Upon confirmation, data is added to the specified Google Sheet.
