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
                    user_id BIGINT,
                    message_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_response TEXT,
                    model_used TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                ''')

                #cursor.execute("DROP TABLE IF EXISTS model_stats")
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_stats (
                    model_name TEXT,
                    user_id BIGINT,
                    response_time REAL,
                    token_used INTEGER,
                    success INTEGER
                )
                ''')

                #cursor.execute("DROP TABLE IF EXISTS documents")
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    filename TEXT,
                    content TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                ''')

                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_model_name ON model_stats(model_name)')

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

    def save_model_metrics(self, user_id, model_name, response_time, token_used, success):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_stats
                    (model_name, user_id, response_time, token_used, success)
                    VALUES (?,?,?,?,?)
                ''', (model_name, user_id, response_time, token_used, success))
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
                        SUM(token_used) as total_tokens,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success
                    FROM model_stats
                    WHERE user_id = ?
                    GROUP BY model_name
                    ORDER BY usage_count DESC
                ''', (user_id,))

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

    def add_document(self, user_id, filename, content):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO documents (user_id, filename, content)
                    VALUES (?,?,?)
                ''', (user_id, filename, content))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления документа: {e}")
            return  None

    def get_user_documents(self, user_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT filename, content, uploaded_at 
                    FROM documents 
                    WHERE user_id = ? 
                    ORDER BY uploaded_at DESC
                ''', (user_id,))

                documents = cursor.fetchall()
                return documents
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения документов: {e}")
            return  None


    def get_document_content(self, document_id, user_id=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if user_id:
                    cursor.execute('''
                        SELECT filename, content, uploaded_at 
                        FROM documents 
                        WHERE id = ? AND user_id = ?
                    ''', (document_id, user_id))
                else:
                    cursor.execute('''
                        SELECT filename, content, uploaded_at 
                        FROM documents 
                        WHERE id = ?
                    ''', (document_id,))

                document = cursor.fetchone()

                if document:
                    return {
                        'filename': document[0],
                        'content': document[1],
                        'uploaded_at': document[2]
                    }
                else:
                    return None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения данных из документа: {e}")
            return  None

    def search_in_documents(self, user_id, query):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query_words = query.split()
                conditions = []
                params = [user_id]

                for word in query_words:
                    if len(word) > 2:
                        conditions.append("content LIKE ?")
                        params.append(f'%{word}%')

                if not conditions:
                    return []

                where_clause = " AND ".join(conditions)

                cursor.execute(f'''
                    SELECT id, filename, content, uploaded_at
                    FROM documents 
                    WHERE user_id = ? AND ({where_clause})
                    ORDER BY ({" + ".join([f"(LENGTH(content) - LENGTH(REPLACE(LOWER(content), LOWER(?), ''))) / LENGTH(?)" for _ in conditions])}) DESC
                ''', params * 2)

                results = []
                for row in cursor.fetchall():
                    doc = {
                        'id': row[0],
                        'filename': row[1],
                        'content': row[2],
                        'uploaded_at': row[3]
                    }
                    results.append(doc)

                return results

        except sqlite3.Error as e:
            logger.error(f"Ошибка поиска в документах: {e}")
            return []


