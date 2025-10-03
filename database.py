import sqlite3
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Таблица пользователей
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                # Таблица сообщений
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_response TEXT,
                    model_used TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                ''')

                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Ошибка!: {e}")

    def add_user(self, user_id, username, first_name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
                ''', (user_id, username, first_name))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False

    def add_message(self, user_id, message_text):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO messages (user_id, message_text)
                VALUES (?, ?)
                ''', (user_id, message_text))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении сообщения: {e}")
            return False

    def get_user_stats(self, user_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Информация о пользователе
                cursor.execute('''
                SELECT username, first_name, first_interaction 
                FROM users WHERE user_id = ?
                ''', (user_id,))
                user_info = cursor.fetchone()

                # Количество сообщений
                cursor.execute('''
                SELECT COUNT(*) FROM messages WHERE user_id = ?
                ''', (user_id,))
                message_count = cursor.fetchone()[0]

                if user_info:
                    return {
                        'username': user_info[0],
                        'first_name': user_info[1],
                        'first_interaction': user_info[2],
                        'message_count': message_count
                    }
                return None


        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return None


    def get_user_messages(self, user_id, limit=5):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                        SELECT message_text, timestamp 
                        FROM messages 
                        WHERE user_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                        ''', (user_id, limit))

                messages = cursor.fetchall()
                return messages

        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении сообщений: {e}")
            return []

    def add_ai_response(self, message_id, ai_response, model_used):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE messages
                SET ai_response = ?, model_used = ?
                WHERE id = ?
                ''', (ai_response, model_used, message_id))
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Ошибка {e}")
            return False
