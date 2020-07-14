import telebot
import requests
from telebot import types
global step
step = 0
bot = telebot.TeleBot('992948925:AAHH7-hvNZNQZr4rYHgsRX6MfcMCeIgwtjw')

def pogoda1(msg, chat_id):
    global step
    s_city = msg
    city_id = 0
    appid = "130569a52163982e4e170c25f28de658"
    res = requests.get("http://api.openweathermap.org/data/2.5/find",
        params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
    global data
    data = res.json()
    if (data['cod'] == '400' or len(data['list']) == 0):
        bot.send_message(chat_id, "Извините, но информации по такому городу нет",
            parse_mode='html')
    elif (len(data['list']) == 1):
        bot.send_message(chat_id, 'Сейчас ' + str(data['list'][0]['main']['temp']) + ' градусов',
            parse_mode='html')
    else:
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
            for d in data['list']]
        global i
        i=0
        bot.send_message(chat_id, "Я нашла следующие города:",
            parse_mode='html')
        while i<len(cities):
            bot.send_message(chat_id, str(i+1)+ ": " + str(cities[i]),
                parse_mode='html')
            i+=1
        bot.send_message(chat_id, "Какой город выбрать?",
            parse_mode='html')
        step = 2

def pogoda2(msg, chat_id):
    try:
        global i
        global data
        p=int(msg)-1
        if (p>-1 and p<i+1):
            bot.send_message(chat_id, 'Сейчас ' + str(data['list'][p]['main']['temp']) + ' градусов',
                parse_mode='html')
        else:
            bot.send_message(chat_id, "Ой, такого номера в списке нет",
                parse_mode='html')
    except Exception:
        bot.send_message(chat_id, "Ой, такого номера в списке нет",
            parse_mode='html')

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Погода")
    item2 = types.KeyboardButton("Закончить")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Привет, <b>{0.first_name}</b>!\nЯ - <b>{1.first_name}</b>, ваша ассистентка.".format(message.from_user, bot.get_me()),
        parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, 'Я умею показывать погоду\nНапишите сообщение "погода" и выберите город, если совпадений несколько, отправьте номер интересующего места\nДля отмены запроса нажмите "закончить"\nВсегда рада вам помочь!',
        parse_mode='html')

@bot.message_handler(content_types=['text'])
def send_text(message):
    global step
    if (message.text == "Закончить"):
        bot.send_message(message.chat.id, "Хорошо",
                parse_mode='html')
        step = 0
    elif (message.text == "Погода"):
        bot.send_message(message.chat.id, "Какой город вас интересует?",
        parse_mode='html')
        step=1
    elif (step == 1):
        chat_id = message.chat.id
        pogoda1(message.text, chat_id)
    elif (step == 2):
        chat_id = message.chat.id
        pogoda2(message.text, chat_id)
    else:
        bot.send_message(message.chat.id, "Я вас не поняла",
            parse_mode='html')
    
bot.polling()
