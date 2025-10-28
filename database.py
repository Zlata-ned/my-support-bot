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
                cursor.execute("DROP TABLE IF EXISTS messages")
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


    def add_ai_response(self, user_id, ai_response=None, model_used=None):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO messages (user_id, ai_response, model_used)
            VALUES (?, ?, ?)
            ''', (user_id, ai_response, model_used))
            message_id=cursor.lastrowid
            conn.commit()
            conn.close()
            return message_id

        except Exception as e:
            logger.error(f"Ошибка {e}")
            return None

    def save_model_metrics(self, user_id, model_name, response_time, tokens_estimate, tokens_used, success):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_stats
                    (model_name, user_id, response_time, tokens_used, success)
                    VALUES (?,?,?,?,?)
                ''', (model_name, user_id, response_time, tokens_estimate, success, tokens_used))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка сохранения метрик: {e}")
            return False

    def get_model_comparison_stats(self, user_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT
                        model_name,
                        COUNT(*) as usage_count,
                        AVG(response_time) as avg_time,
                        SUM(tokens_used) as total_tokens,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success,
                    FROM model_stats
                    WHERE user_id = ?
                    GROUP BY model_name
                    ORDER BY usage_count DESC
                ''', user_id)

                results = cursor.fetchall()
                return [{
                    'model': row[0],
                    'count': row[1],
                    'avg_time': row[2],
                    'tokens': row[3],
                    'success_rate': (row[4] / row[1]*100) if row[1] > 0 else 0
                }for row in results]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return []
