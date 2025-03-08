# stickers.py
from telegram import InputSticker
from config import STICKERS

class StickerManager:
    @staticmethod
    def get_sticker(mood):
        return InputSticker(remote_file_id=STICKERS.get(mood, STICKERS["happy"]))

    @staticmethod
    def send_sticker(update, mood):
        sticker = StickerManager.get_sticker(mood)
        update.message.reply_sticker(sticker)