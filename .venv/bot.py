import telebot
from config import bot

bot = telebot.TeleBot(bot)

@bot.message_handler(commands=['start'])   #Ответ на команду start
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "Привет! Чем я могу тебе помочь?")

@bot.message_handler(commands=['help'])   #Ответ на команду help
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, "Вот список досупных команд: /start, /help, /info")

@bot.message_handler(commands=['info'])   #Ответ на команду info
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id,"Привет! Этот бот работает как эхо. Ты можешь отправить мне любое сообщение, а я повторю его!")

@bot.message_handler(func=lambda message: True)   #Ответ на текстовые сообщения пользователя
def handle_message(message):
    print(message)
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(content_types= ['photo', 'sticker'])  #Обработка изображений и стикеров
def handle_message(message):
    if message.photo:
        bot.send_message(message.chat.id, 'Вы отправили изображение. Я обрабатываю только текстовые сообщения.')

    if message.sticker:
        bot.send_message(message.chat.id, 'Вы отправили стикер. Я обрабатываю только текстовые сообщения.')

bot.polling(none_stop=True)
