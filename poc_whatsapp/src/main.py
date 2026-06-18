import os
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

from .ai_integration import AIProcessor
from .sheets_integration import GoogleSheetsManager

app = FastAPI()

# Load environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "YOUR_VERIFY_TOKEN")
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE")
SHEET_NAME = os.environ.get("SHEET_NAME")

# Initialize services only if API keys are available
ai_processor = None
google_sheets = None

if OPENAI_API_KEY:
    ai_processor = AIProcessor(OPENAI_API_KEY)
if GOOGLE_CREDENTIALS_FILE and SHEET_NAME:
    google_sheets = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, SHEET_NAME)

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return JSONResponse(content={"status": "error"}, status_code=400)

def format_whatsapp_message(product, old_price, new_price):
    message = f"*Price Update:*\n\n*Product:* {product}"
    if old_price is not None:
        message += f"\n*Old Price:* ${old_price:.2f}"
    message += f"\n*New Price:* ${new_price:.2f}"
    return message

async def process_audio_message(audio_url, message_id):
    if not ai_processor or not google_sheets:
        print("Services not fully configured")
        return
    
    audio_path = "./placeholder_audio.ogg"
    
    try:
        text = await ai_processor.transcribe_audio(audio_path)
        extracted_data = await ai_processor.extract_price_data(text)
        if not extracted_data:
            return JSONResponse(content={"status": "error", "message": "Could not extract valid data"}, status_code=400)
        data = json.loads(extracted_data)
        
        product = data.get("product")
        price = data.get("price")
        action = data.get("action")
        
        if not product or price is None or not action:
            return JSONResponse(content={"status": "error", "message": "Could not extract valid data"}, status_code=400)

        old_price = None
        timestamp = datetime.now().isoformat()
        success = await google_sheets.add_price_entry(product, old_price, price, timestamp)
        
        if success:
            formatted_message = format_whatsapp_message(product, old_price, price)
            return JSONResponse(content={"status": "success", "message_to_send": formatted_message}, status_code=200)
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to save to Google Sheets"}, status_code=500)
            
    except Exception as e:
        print(f"Error processing audio: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/webhook")
async def handle_message(request: Request):
    try:
        data = await request.json()
        print(f"Received message: {json.dumps(data, indent=2)}")

        if "object" in data and data["object"] == "whatsapp_business_account":
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]

            if value.get("messages"):
                message = value["messages"][0]
                message_id = message["id"]
                
                if message.get("audio"):
                    audio_url = message["audio"].get("url")
                    asyncio.create_task(process_audio_message(audio_url, message_id))
                    return JSONResponse(content={"status": "received"})
                elif message.get("interactive") and message["interactive"].get("type") == "button_reply":
                    button_id = message["interactive"]["button_reply"].get("id")
                    if button_id == "save":
                        return JSONResponse(content={"status": "success", "message_to_send": "✅ Changes saved!"})
                    elif button_id == "cancel":
                        return JSONResponse(content={"status": "cancelled", "message_to_send": "❌ Action cancelled."})

    except Exception as e:
        print(f"Error handling message: {e}")
        return JSONResponse(content={"status": "error", "message": "Internal server error"}, status_code=500)

    return JSONResponse(content={"status": "received"})
