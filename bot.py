# bot.py
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from config import BOT_SETTINGS, QALAM_API, DICTIONARY_API, EMOJIS
from database import DatabaseManager

db = DatabaseManager()

# ------ وظيفة توليد الرد مع الذاكرة ------
def generate_response(user_id, user_input):
    history = db.get_conversation_history(user_id)
    context = "\n".join(history[::-1])  # عكس الترتيب للحصول على التسلسل الصحيح
    
    payload = {
        "text": user_input,
        "context": f"""
        [شخصية البوت]
        الاسم: {BOT_SETTINGS['NAME']}
        المطعم: {BOT_SETTINGS['RESTAURANT']}
        الموقع: {BOT_SETTINGS['LOCATION']}
        يحب: {', '.join(BOT_SETTINGS['LIKES'])}
        يكره: {', '.join(BOT_SETTINGS['DISLIKES'])}
        
        [المحادثة السابقة]
        {context}
        """
    }
    
    response = requests.post(QALAM_API["URL"], json=payload).json()
    return response.get("reply", "لم أفهم السؤال، حاول مجدداً.")

# ------ معالجة الرسائل مع الحالة المزاجية ------
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text
    
    # تحديث الحالة المزاجية بناءً على الكلمات الرئيسية
    if any(word in user_input for word in ["حزين", "مشكلة", "تعيس"]):
        db.update_mood(user_id, "sad")
    elif any(word in user_input for word in ["غاضب", "غيظ", "زعلان"]):
        db.update_mood(user_id, "angry")
    else:
        db.update_mood(user_id, "happy")
    
    # الحصول على الإيموجي المناسب
    current_mood = db.get_mood(user_id)
    emoji = EMOJIS.get(current_mood, "😐")  # إيموجي محايد إذا لم تُحدد الحالة
    
    # توليد الرد وإرساله مع الإيموجي
    response = generate_response(user_id, user_input)
    update.message.reply_text(f"{emoji} {response}")  # الإيموجي قبل النص
    
    # حفظ المحادثة في الذاكرة
    db.save_conversation(user_id, user_input)

# ------ التشغيل الرئيسي ------
def main():
    updater = Updater(BOT_SETTINGS["TOKEN"], use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        f"مرحباً! أنا {BOT_SETTINGS['NAME']}\n"
        "مطور البوت: @your_username\n"
        "استخدم /help للتعرف على الأوامر"
    )

if __name__ == "__main__":
    main()
