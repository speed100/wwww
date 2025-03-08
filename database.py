# database.py
import sqlite3
from config import QALAM_API

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('data/conversations.db')
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # جدول المحادثات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                user_id INTEGER,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # جدول الحالة المزاجية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moods (
                user_id INTEGER PRIMARY KEY,
                current_mood TEXT DEFAULT 'happy',
                last_updated DATETIME
            )
        ''')
        self.conn.commit()

    def save_conversation(self, user_id, message):
        cursor = self.conn.cursor()
        # حذف الرسائل القديمة للحفاظ على حجم الذاكرة
        cursor.execute('''
            DELETE FROM conversations 
            WHERE user_id = ? AND timestamp < (
                SELECT timestamp 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1 OFFSET ?
            )
        ''', (user_id, user_id, QALAM_API["CONTEXT_LENGTH"]-1))
        # إضافة الرسالة الجديدة
        cursor.execute('INSERT INTO conversations (user_id, message) VALUES (?, ?)', (user_id, message))
        self.conn.commit()

    def get_conversation_history(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT message 
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, QALAM_API["CONTEXT_LENGTH"]))
        return [row[0] for row in cursor.fetchall()]

    def update_mood(self, user_id, mood):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO moods (user_id, current_mood, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, mood))
        self.conn.commit()

    def get_mood(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT current_mood FROM moods WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else "happy"