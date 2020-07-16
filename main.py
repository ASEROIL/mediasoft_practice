import telebot
import requests
import sqlite3

from telebot import types

bot = telebot.TeleBot('992948925:AAHH7-hvNZNQZr4rYHgsRX6MfcMCeIgwtjw')

@bot.message_handler(commands=['start'])
def welcome(message):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?",[message.chat.id])
    if (not(cursor.fetchall())):
        cursor.execute("INSERT INTO users VALUES(?,?)", [message.chat.id,'Москва'])
    conn.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Погода")
    item2 = types.KeyboardButton("Закончить")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Привет, <b>{0.first_name}</b>!\nЯ - <b>{1.first_name}</b>, ваша ассистентка.".format(message.from_user, bot.get_me()),
        parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if (message.text == "Закончить"):
        msg = bot.send_message(message.chat.id, "Хорошо",
                parse_mode='html')
    elif (message.text == "/help"):
        bot.send_message(message.chat.id, 'Я умею показывать погоду\n\nНапишите сообщение "погода" и выберите город, если совпадений несколько, отправьте номер интересующего места\n\nДля отмены запроса нажмите "закончить"\n\nВсегда рада вам помочь!',
        parse_mode='html')
    elif (message.text == "Погода"):
        msg = bot.send_message(message.chat.id, "Какой город вас интересует?",
        parse_mode='html')
        bot.register_next_step_handler(msg,pogoda1)
    else:
        bot.send_message(message.chat.id, "Я вас не поняла",
            parse_mode='html')

@bot.message_handler(content_types=['text'])
def pogoda1(message):
    if (message.text == "Закончить"):
        msg = bot.send_message(message.chat.id, "Хорошо",
                parse_mode='html')
        bot.register_next_step_handler(msg,send_text)
        return
    elif (message.text == "/help"):
        msg = bot.send_message(message.chat.id, 'Я умею показывать погоду\n\nНапишите сообщение "погода" и выберите город, если совпадений несколько, отправьте номер интересующего места\n\nДля отмены запроса нажмите "закончить"\n\nВсегда рада вам помочь!',
            parse_mode='html')
        bot.register_next_step_handler(msg,pogoda1)
        return
    s_city = message.text
    appid = "130569a52163982e4e170c25f28de658"
    res = requests.get("http://api.openweathermap.org/data/2.5/find",
        params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
    data = res.json()
    if (data['cod'] == '400' or len(data['list']) == 0):
        msg = bot.send_message(message.chat.id, "Извините, но информации по такому городу нет",
            parse_mode='html')
        bot.register_next_step_handler(msg,pogoda1)
    elif (len(data['list']) == 1):
        msg = bot.send_message(message.chat.id, 'Сейчас ' + str(data['list'][0]['main']['temp']) + ' градусов',
            parse_mode='html')
        bot.register_next_step_handler(msg,pogoda1)
    else:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET city1 = ? where id = ?", [s_city,message.chat.id])
        conn.commit()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
            for d in data['list']]
        i=0
        bot.send_message(message.chat.id, "Я нашла следующие города:",
            parse_mode='html')
        while i<len(cities):
            bot.send_message(message.chat.id, str(i+1)+ ": " + str(cities[i]),
                parse_mode='html')
            i+=1
        msg = bot.send_message(message.chat.id, "Какой город выбрать?",
            parse_mode='html')
        bot.register_next_step_handler(msg,pogoda2)

@bot.message_handler(content_types=['text'])
def pogoda2(message):
    if (message.text == "Закончить"):
        msg = bot.send_message(message.chat.id, "Хорошо",
                parse_mode='html')
        bot.register_next_step_handler(msg,send_text)
        return
    elif (message.text == "/help"):
        msg = bot.send_message(message.chat.id, 'Я умею показывать погоду\n\nНапишите сообщение "погода" и выберите город, если совпадений несколько, отправьте номер интересующего места\n\nДля отмены запроса нажмите "закончить"\n\nВсегда рада вам помочь!',
            parse_mode='html')
        bot.register_next_step_handler(msg,pogoda2)
        return
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT city1 FROM users WHERE id = ?",[message.chat.id])
    s_city = cursor.fetchall()[0][0]
    appid = "130569a52163982e4e170c25f28de658"
    res = requests.get("http://api.openweathermap.org/data/2.5/find",
        params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': appid})
    data = res.json()
    try:
        p=int(message.text)-1
        if (p>-1 and len(data['list'])):
            bot.send_message(message.chat.id, 'Сейчас ' + str(data['list'][p]['main']['temp']) + ' градусов',
                parse_mode='html')     
        else:
            msg = bot.send_message(message.chat.id, "Ой, такого номера в списке нет",
                parse_mode='html')            
    except Exception:
        msg = bot.send_message(message.chat.id, "Ой, такого номера в списке нет",
                parse_mode='html')
    msg = bot.send_message(message.chat.id, "Какой город еще выбрать?",
        parse_mode='html')
    bot.register_next_step_handler(msg,pogoda2)
    
bot.polling()
