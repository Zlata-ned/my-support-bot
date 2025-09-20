from datetime import datetime
import telebot
import random
from config import bot_token, db_name
from database import Database, logger

bot = telebot.TeleBot(bot_token)
db = Database(db_name)

joke = ['Приделали одноногому колесо и пошло поехало','-Блин! - сказал слон, наступив на колобка','Мало кто знает, что  после того, как Иван Грозный убил своего сына, он еще спалил дом и срубил дерево','Сын директора фабрики по изготовлению туалетной бумаги всегда в костюме мумии']

@bot.message_handler(commands=['start'])   #Ответ на команду start
def com_start(message):
    print(message)
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    bot.send_message(message.chat.id, "Привет! Чем я могу тебе помочь?")

@bot.message_handler(commands=['help'])   #Ответ на команду help
def com_help(message):
    print(message)
    bot.send_message(message.chat.id, "🤖 Досупные команды: \n /start - Начать работу с ботом \n /history - показать последние 5 сообщений \n /stats - показывает статистику \n /help - Показать это сообщение\n /info - Информация о боте\n /time - Показать текущее время\n /joke - Рассказать шутку\n /weather - Информация о погоде\n /about - О создателе бота")

@bot.message_handler(commands=['info'])   #Ответ на команду info
def com_info(message):
    print(message)
    bot.send_message(message.chat.id,"Привет! Этот бот работает как эхо. Ты можешь отправить мне любое сообщение, а я повторю его!💞")

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

@bot.message_handler(commands=['about'])   #Ответ на команду about
def com_about(message):
    print(message)
    bot.send_message(message.chat.id, "Создатель: Злата Н.\nВерсия: 2.0\nСоздан: 06.09.2025")

@bot.message_handler(func=lambda message: True)   #Обработка неизвестных команд
def answer_message(message):
    if message.text[0] !="/":
        print(message)
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
