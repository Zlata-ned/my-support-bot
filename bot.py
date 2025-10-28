from datetime import datetime
import telebot
import random
from config import bot_token, db_name
from database import Database, logger
from ai_service import ai_manager

bot = telebot.TeleBot(bot_token)
db = Database(db_name)

user_modes = {}


joke = ['Приделали одноногому колесо и пошло поехало','-Блин! - сказал слон, наступив на колобка','Мало кто знает, что  после того, как Иван Грозный убил своего сына, он еще спалил дом и срубил дерево','Сын директора фабрики по изготовлению туалетной бумаги всегда в костюме мумии']

@bot.message_handler(commands=['start'])   #Ответ на команду start
def com_start(message):
    print(message)
    user_modes[message.from_user.id] = "echo"
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    bot.send_message(message.chat.id, "Привет! Чем я могу тебе помочь?")

@bot.message_handler(commands=['help'])   #Ответ на команду help
def com_help(message):
    print(message)
    bot.send_message(message.chat.id, "🤖 Досупные команды: \n /start - Начать работу с ботом \n /smart - переключение бота на режим ИИ \n /echo - переключение бота на режим эхо \n /model_info - информация о модели \n /switch [номер] - переключить модель \n /compare [вопрос] - сравнить ответы всех моделей \n /model_stats - показывает статистику использования моделей \n /benchmark - запустить полный тест производительности \n /ai [вопрос] - вопрос ИИ \n /history - показать последние 5 сообщений \n /stats - показывает статистику \n /help - Показать это сообщение\n /info - Информация о боте\n /time - Показать текущее время\n /joke - Рассказать шутку\n /weather - Информация о погоде\n /about - О создателе бота")

@bot.message_handler(commands=['info'])   #Ответ на команду info
def com_info(message):
    print(message)
    bot.send_message(message.chat.id,"Привет! Этот бот работает как эхо. Ты можешь отправить мне любое сообщение, а я повторю его!💞")

@bot.message_handler(commands=['models']) #Ответ на команду models
def com_models(message):
    print(message)
    bot.send_message(message.chat.id, "🤖 Досупные модели: \n\n 1.DeepSeek Chat \n └─ Провайдер: DeepSeek \n └─ Скорость: Средняя \n └─ Стоимость: Платная \n\n 2.Llama 3.1 8B (Groq) \n └─ Провайдер: Groq \n └─ Скорость: Очень быстрая \n └─ Стоимость: Беслатная \n\n 3.Llama 3 8B (Together) \n └─ Провайдер: Groq \n └─ Скорость: Очень быстрая \n └─ Стоимость: Беслатная")

@bot.message_handler(commands=['stats'])   #Ответ на команду stats
def com_stats(message):
    print(message)
    stats = db.get_user_stats(message.from_user.id)
    if stats:
        bot.send_message(message.chat.id, "Ваша статистика: \n"
                                          f"Имя: {stats['first_name']}\n"
                                          f"Первое сообщение: {stats['first_interaction']}\n"
                                          f"Всего сообщений: {stats['message_count']}\n"
                                          f"User ID: {message.from_user.id}\n"
                         )
    else:
        bot.send_message(message.chat.id,"Информация о вас не найдена")

@bot.message_handler(commands=['ai'])   #Ответ на команду ai
def com_ai(message):
    print(message)
    if len(message.text.strip()) <= 3:
        bot.reply_to(message, "Вам нужно написать вопрос после команды /ai!")
        return
    question = message.text[4:].strip()
    if not question:
        bot.reply_to(message, "Вам нужно написать вопрос после команды /ai!")
        return
    ai_response = ai_manager.get_response(question, message.from_user.first_name)

    if ai_response['success']:
        bot.reply_to(message,
                     f"{ai_response['response'].choices[0].message.content}\n\n"
                     f"Время: {ai_response['time']:.2f} сек\n\n"
                     f"Модель: {ai_response['model']}"
                     )
    else:
        bot.reply_to(message, ai_response)

    db.add_ai_response(
        user_id=message.from_user.id,
        ai_response=ai_response['response'].choices[0].message.content,
        model_used=ai_response['model']

    )

    db.save_model_metrics(
        model_name=ai_response['model'],
        user_id=message.from_user.id,
        response_time=ai_response['time'],
        success=ai_response['success'],
        token_used=ai_response["response"].usage.total_tokens
    )

@bot.message_handler(commands=['smart'])   #Ответ на команду smart
def com_smart(message):
    print(message)
    user_modes[message.from_user.id] = "ai"
    bot.reply_to(message, "Режим переключен на AI")

@bot.message_handler(commands=['echo'])   #Ответ на команду echo
def com_echo(message):
    print(message)
    user_modes[message.from_user.id] = "echo"

@bot.message_handler(commands=['model_info'])   #Ответ на команду model_info
def com_model_info(message):
    print(message)
    current_mode = user_modes.get(message.from_user.id, "echo")
    bot.reply_to(message, "Информация о модели:\nМодель: DeepSeek Chat\nВаш режим: ИИ" if current_mode == 'ai' else 'Эхо')

@bot.message_handler(commands=['joke']) #Ответ на команду joke
def com_joke(message):
    print(message)
    bot.send_message(message.chat.id, random.choice(joke))

@bot.message_handler(commands=['history'])   #Ответ на команду stats
def com_history(message):
    print(message)
    messages = db.get_user_messages(message.from_user.id)
    if messages:
        for i, (text, timestamp) in enumerate(messages, 1):
            bot.send_message(message.chat.id, "Ваши последние сообщения: \n"
                                                    f"{i}. {text}")
    else:
            bot.send_message(message.chat.id, "У вас пока нет сохраненных сообщений")


@bot.message_handler(commands=['time'])   #Ответ на команду time
def com_time(message):
    print(message)
    bot.send_message(message.chat.id, datetime.now().strftime("%H:%M:%S") )

@bot.message_handler(commands=['weather'])   #Ответ на команду weather
def com_weather(message):
    print(message)
    bot.send_message(message.chat.id, "К сожалению, я пока не умею показывать погоду, но скоро научусь! ⛅")

@bot.message_handler(commands=['model_stats'])    #Ответ на команду model_stats
def com_model_stats(message):
    stats = db.get_model_comparison_stats(message.from_user.id)
    if not stats:
        bot.reply_to(message, "У вас пока нет статистики использования моделей")
        return

    response = "📊 Ваша статистика моделей:\n\n"
    for stat in stats:
        response += f"🤖 {stat['model']}:\n"
        response += f"├─ Использовано: {stat['count']} раз\n"
        response += f"├─ Среднее время: {stat['avg_time']:.2f} сек\n"
        response += f"├─ Токенов: ~{stat['tokens']}\n"
        response += f"└─ Успешность: {stat['success_rate']:.1f}%\n\n"

    fastest = min(stats, key=lambda x: x['avg_time'])
    most_used = max(stats, key=lambda x: x['count'])


    response += f"Самая быстрая: {fastest['model']} ({fastest['avg_time']})"
    response += f"Самая используемая: {most_used['model']} ({most_used['count']})"

    bot.reply_to(message, response)

@bot.message_handler(commands=['compare'])    #Ответ на команду compare
def com_compare(message):
    question = message.text[9:].strip()
    if not question:
        bot.reply_to(message, "Напиши вопрос после /compare")
        return

    status_msg = bot.reply_to(message, "⏳ Отправляю запрос всем моделям")

    results = ai_manager.compare_all(question)

    response = "Результаты сравнения:"
    times = []

    for i, (model_name, result) in enumerate(results.items(), 1):
        response += f"{i}️⃣ {result['info']['name']}\n"
        if result['success']:
            response += f"{result['time']: .2f} сек\n"
            times.append((model_name, result['time']))

        else:
            response += f"{result['response']}\n\n"

    if times:
        fastest = min(times, key=lambda x: x[1])
        response += f"\n Самая быстрая: {fastest[0]} ({fastest[1]:.2f} сек)"

    bot.edit_message_text(response, message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['benchmark'])    #Ответ на команду benchmark
def com_benchmark(message):
    test_questions = [
        "Объясни что такое рекурсия простыми словами",
        "Расскажи короткую шутку про программистов",
        "Реши: 123 * 456 = ?"
    ]

    status_msg = bot.reply_to(message, "🔬 Запускаю бенчмарк...")

    all_results = {}

    for question in test_questions:
        results = ai_manager.compare_all(question)
        for model_name, result in results.items():
            if model_name not in all_results:
                all_results[model_name] = []
            if result['success']:
                all_results[model_name].append(result['time'])

    response = "Результаты бенчмарка:\n\n"

    avg_times = {}
    for model_name, times in all_results.items():
        if times:
            avg_time = sum(times) / len(times)
            avg_times[model_name] = avg_time
            response += f"{model_name}:\n"
            response += f"Среднее время: {avg_time:.2f} сек\n\n"

    if avg_times:
        fastest = min(avg_times.items(), key=lambda x: x[1])
        slowest = max(avg_times.items(), key=lambda x: x[1])

        response += f"Самая быстрая: {fastest[0]} ({fastest[1]:.2f} сек) \n"
        response += f"Самая медленная: {slowest[0]} ({slowest[1]:.2f} сек)"

    bot.edit_message_text(response, message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['switch'])   #Ответ на команду about
def com_switch(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Укажите номер модели")
            return

        model_number = int(parts[1])
        services = ai_manager.get_all_services()

        if model_number < 1 or model_number > len(services):
            bot.reply_to(message, f"Номер должен быть от 1 до {len(services)}")
            return

        service_name = services[model_number - 1]
        success = ai_manager.switch_service(service_name)
        if success:
            info = ai_manager.get_service_info(service_name)
            bot.reply_to(message, f"Переключено на: {info['name']}")
        else:
            bot.reply_to(message, "Ошибка переключения модели")

    except ValueError:
        bot.reply_to(message, "Укажите номер цифрой!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка! {str(e)}")

@bot.message_handler(commands=['about'])   #Ответ на команду about
def com_about(message):
    print(message)
    bot.send_message(message.chat.id, "Создатель: Злата Н.\nВерсия: 2.0\nСоздан: 06.09.2025")

@bot.message_handler(func=lambda message: True)   #Обработка неизвестных команд
def answer_message(message):
    if message.text[0] !="/":
        print(message)
        current_mode = user_modes.get(message.from_user.id, "echo")
        if current_mode == "ai":
            ai_response = ai_manager.get_response(message.text, message.from_user.first_name)
            db.add_ai_response(
                user_id=message.from_user.id,
                ai_response=ai_response['response'].choices[0].message.content,
                model_used=ai_response['model']

            )

            db.save_model_metrics(
                model_name=ai_response['model'],
                user_id=message.from_user.id,
                response_time=ai_response['time'],
                success=ai_response['success'],
                token_used=ai_response["response"].usage.total_tokens
            )
            bot.reply_to(message, ai_response['response'].choices[0].message.content)
        else:
            bot.send_message(message.chat.id, message.text)
        db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    else:
        bot.send_message(message.chat.id, "❌ Неизвестная команда. Используй /help для просмотра доступных команд.")

@bot.message_handler(func=lambda message: True, content_types=['text'])   #
def add_text_message(message):
    if message.text[0] == "/":
        return

    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    if db.add_message(message.from_user.id, message.text):
        logger.info(msg="done")
    else:
        logger.error()


@bot.message_handler(content_types= ['photo', 'sticker'])  #Обработка изображений и стикеров
def photo_sticker(message):
    if message.photo:
        bot.send_message(message.chat.id, 'Вы отправили изображение. Пока что я обрабатываю только текстовые сообщения 😕.')

    if message.sticker:
        bot.send_message(message.chat.id, 'Вы отправили стикер. Пока что я обрабатываю только текстовые сообщения 😕.')

bot.polling(none_stop=True)
