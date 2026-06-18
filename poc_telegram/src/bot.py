import os
import csv
import json
import telebot
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import httpx

from ai_integration import AIProcessor

# Cargar variables de entorno
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/price_update")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no configurado. Asegúrate de que el archivo /app/poc_telegram/src/.env esté presente.")

bot = telebot.TeleBot(TOKEN)
ai = AIProcessor(OPENAI_API_KEY) if OPENAI_API_KEY else None

# Local backup CSV file path
LOCAL_CSV_PATH = "cuaderno_precios.csv"
pending_data = {}

def init_csv():
    if not os.path.exists(LOCAL_CSV_PATH):
        with open(LOCAL_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha/Hora", "Producto", "Precio Nuevo", "Acción"])

init_csv()

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "¡Hola! Estoy listo. Envíame un audio con la actualización de un precio y te ayudaré a guardarlo. Usa /descargar para bajarte la planilla.")

@bot.message_handler(commands=['descargar'])
def download_excel(message):
    if os.path.exists(LOCAL_CSV_PATH):
        with open(LOCAL_CSV_PATH, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="Aquí tienes tu cuaderno virtual actualizado. 📊")
    else:
        bot.reply_to(message, "El cuaderno aún está vacío.")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    if not ai:
        bot.reply_to(message, "❌ El procesador de IA no está configurado (falta API_KEY).")
        return

    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    voice_path = "voice.ogg"
    with open(voice_path, 'wb') as f:
        f.write(downloaded_file)
        
    try:
        text = asyncio.run(ai.transcribe_audio(voice_path))
        extracted = asyncio.run(ai.extract_price_data(text))
        data = json.loads(extracted)
        
        if "error" in data:
            bot.reply_to(message, "⚠️ No pude entender el precio o producto. Intenta decirlo de nuevo.")
            return
            
        pending_data[message.from_user.id] = data
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ SÍ, GUARDAR", callback_data="save"))
        markup.add(types.InlineKeyboardButton("❌ NO, CANCELAR", callback_data="cancel"))
        
        reply = f"📝 *Datos detectados:* \n\n🏷️ Producto: {data.get('product')}\n💰 Precio: ${data.get('price')}\n🔄 Acción: {data.get('action')}\n\n¿Es correcto?"
        bot.reply_to(message, reply, parse_mode="Markdown", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error interno: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if call.data == "save":
        data = pending_data.get(user_id)
        if data:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(LOCAL_CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, data.get('product'), data.get('price'), data.get('action')])
            
            bot.edit_message_text("✅ ¡Guardado con éxito! Usa /descargar para obtener el Excel.", chat_id=call.message.chat.id, message_id=call.message.message_id)
            del pending_data[user_id]
    elif call.data == "cancel":
        bot.edit_message_text("❌ Operación cancelada.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        if user_id in pending_data:
            del pending_data[user_id]

if __name__ == "__main__":
    print("Bot en marcha...")
    bot.infinity_polling()
