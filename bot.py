import telebot
import requests
from time import sleep
import json

bot = telebot.TeleBot('YOUR TELEGRAM BOT API KEY')

kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
btn = telebot.types.KeyboardButton(text='Інформація про посилку')
btn1 = telebot.types.KeyboardButton(text='Переваги бота')
kb.add(btn, btn1)

@bot.message_handler(commands=['start'])
def get_command(message):
    if message.text == '/start':
        if message.from_user.last_name:
            bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name} {message.from_user.last_name}! Я бот котрий відслідковує посилки Нової Пошти. Для того щоб отримати інформацію про посилку - натисніть на кнопку "Інформація про посилку".', reply_markup=kb)
        else:
            bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name}! Я бот котрий відслідковує посилки Нової Пошти. Для того щоб отримати інформацію про посилку - натисніть на кнопку "Інформація про посилку".', reply_markup=kb)

@bot.message_handler(content_types=['text'])
def get_information(message):
    if message.text == 'Інформація про посилку':
        bot.send_message(message.chat.id, 'Введіть номер посилки без пробілів.')
        bot.register_next_step_handler(message, novaposhta_request)
    elif message.text == 'Переваги бота':
        bot.send_message(message.chat.id, f'⏰ Час відстеження: 2-3 секунди. \n\n📱 Зручність користування: На всіх пристроях. \n\n💰 Вартість трекінгу: Безкоштовно. \n\n✅ Реєстрація: Не потрібна. \n\n🎯 Точність даних: Гарантовано через API. \n\n🥷 Анонімність: Дані не зберігаються.')
    else:
        pass

def novaposhta_request(message):
    parcel = message.text.replace(' ', '')
    if parcel.isdigit():
        api_url = 'https://api.novaposhta.ua/v2.0/json/'
        json_data = {
            "apiKey": "YOUR NOVAPOST API KEY",
            "modelName": "TrackingDocument",
            "calledMethod": "getStatusDocuments",
            "methodProperties": {"Documents": [{"DocumentNumber": f"{parcel}"}]}
        }

        r = requests.post(url=api_url, json=json_data)

        if r.status_code == 200:
            request = bot.send_message(message.chat.id, 'Отримую інформацію...')
            sleep(2)
            bot.delete_message(message.chat.id, request.message_id)

            # prepare answer to user
            try:
                payload = json.loads(r.text)
                p = payload['data'][0]
                if not p['DocumentCost']:
                    answer = f"Статус посилки: {p['Status']}\n\nМісто відправник: \"{p['CitySender']}\".\nМісто отримувач: \"{p['CityRecipient']}\".\n\nДата створення: {p['DateCreated']}.\nДата доставки: {p['ScheduledDeliveryDate']}.\n\nВага: {p['FactualWeight']}.\nВартість доставки: Безкоштовно."
                else:
                    answer = f"Статус посилки: {p['Status']}\n\nМісто відправник: \"{p['CitySender']}\".\nМісто отримувач: \"{p['CityRecipient']}\".\n\nДата створення: {p['DateCreated']}.\nДата доставки: {p['ScheduledDeliveryDate']}.\n\nВага: {p['FactualWeight']}.\nВартість доставки: {p['DocumentCost']}грн."
                bot.send_message(message.chat.id, answer)
            except IndexError:
                bot.send_message(message.chat.id, 'Такого номера накладної немає, спробуйте ще раз.')
                bot.register_next_step_handler(message, novaposhta_request)
        else:
            bot.send_message(message.chat.id, 'Помилка при отриманні даних про посилку.')
    elif message.text == '/start':
        if message.from_user.last_name:
            bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name} {message.from_user.last_name}! Я бот котрий відслідковує посилки Нової Пошти. Для того щоб отримати інформацію про посилку - натисніть на кнопку "Інформація о посилці".', reply_markup=kb)
        else:
            bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name}! Я бот котрий відслідковує посилки Нової Пошти. Для того щоб отримати інформацію про посилку - натисніть на кнопку "Інформація о посилці".', reply_markup=kb)
    elif message.text == 'Інформація про посилку':
        bot.send_message(message.chat.id, 'Введіть номер посилки.')
        bot.register_next_step_handler(message, novaposhta_request)
    else:
        bot.send_message(message.chat.id, 'Номер посилки повинен бути тільки з цифр.')
        bot.register_next_step_handler(message, novaposhta_request)

bot.infinity_polling()
