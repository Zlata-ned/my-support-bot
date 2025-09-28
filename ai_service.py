import openai
from config import deepseek_api_key
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = openai.OpenAI (
            api_key = deepseek_api_key,
            base_url = "https://api.deepseek.com"
        )
    def get_response(self, user_message, user_name='Пользователь'):
        try:
            response = self.client.chat.completions.create(
                model = "deepseek-chat",
                messages = [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content
            return ai_response
        except Exception as e:
            logger.error(f"Ошибка!{e}")
            return "Извините, ИИ временно не доступен. Попробуйте позже"
ai_service = AIService()