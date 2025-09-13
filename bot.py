import datetime
import telebot
import random
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("bot_token")

bot = telebot.TeleBot(bot_token)
joke = ['Приделали одноногому колесо и пошло поехало','-Блин! - сказал слон, наступив на колобка','Мало кто знает, что  после того, как Иван Грозный убил своего сына, он еще спалил дом и срубил дерево','Сын директора фабрики по изготовлению туалетной бумаги всегда в костюме мумии']


@bot.message_handler(commands=['start'])   #Ответ на команду start
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "Привет! Чем я могу тебе помочь?")

@bot.message_handler(commands=['help'])   #Ответ на команду help
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "🤖 Досупные команды: \n /start - Начать работу с ботом \n /help - Показать это сообщение\n /info - Информация о боте\n /time - Показать текущее время\n /joke - Рассказать шутку\n /weather - Информация о погоде\n /about - О создателе бота")

@bot.message_handler(commands=['info'])   #Ответ на команду info
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id,"Привет! Этот бот работает как эхо. Ты можешь отправить мне любое сообщение, а я повторю его!💞")

@bot.message_handler(commands=['joke'])   #Ответ на команду joke
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, random.choice(joke))

@bot.message_handler(commands=['time'])   #Ответ на команду time
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, datetime.now().strftime("%H:%M:%S") )

@bot.message_handler(commands=['weather'])   #Ответ на команду weather
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "К сожалению, я пока не умею показывать погоду, но скоро научусь! ⛅")

@bot.message_handler(commands=['about'])   #Ответ на команду about
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "Создатель: Злата Н.\nВерсия: 2.0\nСоздан: 06.09.2025")

@bot.message_handler()   #Обработка неизвестных команд
def handle_start(message):
    if message.text[0] =="/":
        bot.send_message(message.chat.id,"❌ Неизвестная команда. Используй /help для просмотра доступных команд.")

@bot.message_handler(func=lambda message: True)   #Ответ на текстовые сообщения пользователя
def handle_message(message):
    print(message)
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(content_types= ['photo', 'sticker'])  #Обработка изображений и стикеров
def handle_message(message):
    if message.photo:
        bot.send_message(message.chat.id, 'Вы отправили изображение. Пока что я обрабатываю только текстовые сообщения 😕.')

    if message.sticker:
        bot.send_message(message.chat.id, 'Вы отправили стикер. Пока что я обрабатываю только текстовые сообщения 😕.')

bot.polling(none_stop=True)
