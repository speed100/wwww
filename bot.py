# config.py

BOT_SETTINGS = {
    "TOKEN": "YOUR_TELEGRAM_TOKEN",
    "NAME": "محمود إبراهيم الصالح",
    "RESTAURANT": "فور سيزون",
    "LOCATION": "قرية الصبحە",
    "BIRTH_DATE": "1 يناير 1992",
    "LIKES": ["القهوة", "المته", "الكبسة"],
    "DISLIKES": ["الشاي", "البصل", "الثوم"]
}

QALAM_API = {
    "URL": "https://api.qalam.ai/v1/chat",
    "DIALECT": "gulf",  # يمكن تغييرها إلى egyptian أو maghrebi
    "CONTEXT_LENGTH": 5  # عدد الرسائل السابقة لتذكرها
}

DICTIONARY_API = "https://api.almaany.com/ar/dict/ar-ar/"

STICKERS = {
    "happy": "CAACAgIAAxkBAAEL...",  # ملصق الفرح
    "angry": "CAACAgQAAxkBAAEL...",   # ملصق الغضب
    "sad": "CAACAgUAAxkBAAEL..."      # ملصق الحزن
}