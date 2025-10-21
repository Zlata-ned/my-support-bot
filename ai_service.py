import openai
import time
import requests
from config import deepseek_api_key, TOGETHER_API_KEY, GROQ_API_KEY
import logging

logger = logging.getLogger(__name__)

class BaseAIService:
    def get_response(self, user_message, user_name='Пользователь'):
        raise NotImplementedError
    def get_model_info(self):
        raise NotImplementedError

class DeepSeekService(BaseAIService):
    def __init__(self):
        self.client = openai.OpenAI (
            api_key = deepseek_api_key,
            base_url = "https://api.deepseek.com"
        )
        self.model_name = "deepseek-chat"
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
            return "Извините, DeepSeek временно не доступен. Попробуйте позже"
    def get_model_info(self):
        return {
            "name": "DeepSeek Chat",
            "type": "Облачная",
            "provider": "DeepSeek",
            "cost": "Платная",
            "speed": "Средняя"
        }
class GroqService(BaseAIService):
    def __init__(self):
        self.client = openai.OpenAI (
            api_key = GROQ_API_KEY,
            base_url = "https://api.groq.com/openai/v1"
        )
        self.model_name = "llama-3.1-8b-instant"
    def get_response(self, user_message, user_name='Пользователь'):
        try:
            response = self.client.chat.completions.create(
                model = self.model_name,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1024,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content
            return ai_response
        except Exception as e:
            logger.error(f"Ошибка Groq!{e}")
            return "Извините, Groq временно не доступен. Попробуйте позже"
    def get_model_info(self):
        return {
            "name": "Llama 3.1 8B (Groq)",
            "type": "Облачная",
            "provider": "Groq",
            "cost": "Бесплатная",
            "speed": "Очень быстрая"
        }
class TogetherService(BaseAIService):
    def __init__(self):
        self.client = openai.OpenAI (
            api_key = TOGETHER_API_KEY,
            base_url = "https://api.together.xyz/v1"
        )
        self.model_name = "meta-llama/llama-3.1-8b-chat-hf"
    def get_response(self, user_message, user_name='Пользователь'):
        try:
            response = self.client.chat.completions.create(
                model = self.model_name,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1024,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content
            return ai_response
        except Exception as e:
            logger.error(f"Ошибка Together!{e}")
            return "Извините, Together временно не доступен. Попробуйте позже"
    def get_model_info(self):
        return {
            "name": "Llama 3.1 8B (Together)",
            "type": "Облачная",
            "provider": "Together AI",
            "cost": "Бесплатная (лимит)",
            "speed": "Очень быстрая"
        }
class AIManager:
    def __init__(self):
        self.services = {
            "deepseek": DeepSeekService(),
            "groq_llama": GroqService(),
            "together_llama": TogetherService()
        }
        self.current_service = "deepseek"

    def get_response(self, user_message, user_name='Пользователь'):
        service = self.services[self.current_service]
        start_time = time.time()

        try:
            response = service.get_response(user_message, user_name)
            response_time = time.time() - start_time

            return {
                "response": response,
                "model": self.current_service,
                "time": response_time,
                "success": True
            }
        except Exception as e:
            logger.error(f"Ошибка в {self.current_service}: {e}")
            return {
                "response": f"Ошибка: {str(e)}",
                "model": self.current_service,
                "time": 0,
                "success": False
            }

    def switch_service(self, service_name):
        if service_name in self.services:
            self.current_service = service_name
            return True
        return False

    def get_service_info(self, service_name):
        if service_name in self.services:
            return self.services[service_name].get_model_info()
        return None

    def get_all_services(self):
        return list(self.services.keys())

    def compare_all(self, user_message):
        results = {}
        for name, service in self.services.items():
            start_time = time.time()
            try:
                response = service.get_response(user_message)
                response_time = time.time() - start_time
                results[name] = {
                    "response": response,
                    "time": response_time,
                    "info": service.get_model_info(),
                    "success": True
                }
            except Exception as e:
                results[name] = {
                "response": f"Ошибка: {str(e)}",
                "time": 0,
                "info": service.get_model_info(),
                "success": False
                }
        return results

ai_manager = AIManager()

