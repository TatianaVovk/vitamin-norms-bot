# bot.py — Телеграм-бот для поиска норм потребления витаминов и микроэлементов
# Использует два документа: АУП2 и ТР ТС 022/2011
# Пользователь выбирает документ перед поиском

import pandas as pd
import telebot
import re

# Загрузка данных из Excel
aup2_data = pd.read_excel('data/АУП2.xlsx')
tr_data = pd.read_excel('data/ТР ТС 022.2011.xlsx')

bot = telebot.TeleBot('YOUR_BOT_TOKEN')
current_document = ""

@bot.message_handler(commands=['start'])
def start(message):
    global current_document
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.KeyboardButton('Единые санитарно-эпидемиологические и гигиенические требования'),
        telebot.types.KeyboardButton('ТР ТС 022/2011')
    )
    bot.send_message(
        message.chat.id,
        'Привет! Я твой бот-помощник TV. Я помогу найти нормы потребления по документам:

'
        '1 — Единые санитарно-эпидемиологические и гигиенические требования
'
        '2 — ТР ТС 022/2011

'
        '🔎 Вводи точное название с маленькой буквы для 100% совпадения.
'
        '🔍 Или используй заглавную — покажу всё похожее.',
        reply_markup=markup
    )
    current_document = ""

@bot.message_handler(func=lambda message: message.text in [
    'Единые санитарно-эпидемиологические и гигиенические требования',
    'ТР ТС 022/2011'])
def get_data(message):
    global current_document
    current_document = message.text
    bot.send_message(message.chat.id, 'Введите запрос:')

@bot.message_handler(func=lambda message: len(current_document) > 0)
def search_data(message):
    global current_document
    query = re.sub('[^a-zA-Zа-яА-Я0-9 ]+', '', message.text)
    result = pd.DataFrame()

    if current_document == 'Единые санитарно-эпидемиологические и гигиенические требования':
        result = aup2_data[aup2_data['Название:'].str.contains(query, case=False)]
    elif current_document == 'ТР ТС 022/2011':
        result = tr_data[tr_data['Название:'].str.contains(query, case=False)]

    if not result.empty:
        if len(result) == 1 and result.iloc[0]['Название:'].lower() == query.lower():
            bot.send_message(message.chat.id, 'Результат:
' + str(dict(result.iloc[0])))
        else:
            bot.send_message(message.chat.id, 'Результат:')
            for _, row in result.iterrows():
                bot.send_message(message.chat.id, str(dict(row)))
    else:
        bot.send_message(message.chat.id, 'Информация не найдена.')

bot.polling()
