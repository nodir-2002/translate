from deep_translator import GoogleTranslator
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from deep_translator import GoogleTranslator
import speech_recognition as sr
import os
TOKEN = os.getenv("TOKEN")

user_lang = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="en"),
        ]
    ]

    await update.message.reply_text(
        "👋 Salom! Botga xush kelibsiz!\nTilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- LANGUAGE ----------------
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data
    user_lang[query.from_user.id] = lang

    await query.edit_message_text(f"✅ Til tanlandi: {lang.upper()}")

# ---------------- VOICE TO TEXT ----------------
def voice_to_text(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except:
        return None

# ---------------- TRANSLATE ----------------
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id

    text = message.text if message.text else message.caption

    # 🔊 VOICE HANDLER
    if message.voice:
        file = await message.voice.get_file()
        file_path = "voice.ogg"
        await file.download_to_drive(file_path)

        text = voice_to_text(file_path)
        os.remove(file_path)

        if not text:
            await message.reply_text("❌ Ovoz tushunilmadi")
            return

    # 📄 FILE HANDLER (.txt)
    if message.document:
        file = await message.document.get_file()
        file_path = "file.txt"
        await file.download_to_drive(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        os.remove(file_path)

    if not text:
        await message.reply_text("❌ Matn topilmadi")
        return

    target_lang = user_lang.get(user_id, "uz")

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        await message.reply_text(f"🌐 Tarjima ({target_lang}):\n{translated}")
    except:
        await message.reply_text("❌ Xatolik yuz berdi")

# ---------------- MAIN ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language))

# text + caption + voice + file
app.add_handler(MessageHandler(
    filters.TEXT | filters.CAPTION | filters.VOICE | filters.Document.ALL,
    translate_text
))

print("🚀 SUPER PRO BOT ishga tushdi...")
app.run_polling()
