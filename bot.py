from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from config import BOT_SETTINGS, QALAM_API, DICTIONARY_API, EMOJIS
from database import DatabaseManager
from flask import Flask
import threading
import os

# ------ إعداد خادم ويب للحفاظ على التشغيل 24/7 ------
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بشكل سليم! 🚀"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# ------ إعداد البوت ------
db = DatabaseManager()

def generate_response(user_id, user_input):
    history = db.get_conversation_history(user_id)
    context = "\n".join(history[::-1])
    
    payload = {
        "text": user_input,
        "context": f"""
        الاسم: {BOT_SETTINGS['NAME']}
        المطعم: {BOT_SETTINGS['RESTAURANT']}
        الموقع: {BOT_SETTINGS['LOCATION']}
        يحب: {', '.join(BOT_SETTINGS['LIKES'])}
        يكره: {', '.join(BOT_SETTINGS['DISLIKES'])}
        المحادثة السابقة: {context}
        """
    }
    
    response = requests.post(QALAM_API["URL"], json=payload).json()
    return response.get("reply", "لم أفهم السؤال، حاول مرة أخرى.")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text
    
    # تحديث الحالة المزاجية
    if any(word in user_input for word in ["حزين", "مشكلة", "تعيس"]):
        db.update_mood(user_id, "sad")
    elif any(word in user_input for word in ["غاضب", "غيظ", "زعلان"]):
        db.update_mood(user_id, "angry")
    else:
        db.update_mood(user_id, "happy")
    
    # توليد الرد مع الإيموجي
    current_mood = db.get_mood(user_id)
    emoji = EMOJIS.get(current_mood, "😐")
    response = generate_response(user_id, user_input)
    
    update.message.reply_text(f"{emoji} {response}")
    db.save_conversation(user_id, user_input)

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"مرحباً! أنا {BOT_SETTINGS['NAME']}، مساعدك الشخصي 🍕\n"
        "أساعدك في الإجابة على الأسئلة والتعريفات العربية."
    )

def main():
    # بدء خادم الويب في خيط منفصل
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # بدء بوت التليجرام
    updater = Updater(BOT_SETTINGS["TOKEN"], use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
