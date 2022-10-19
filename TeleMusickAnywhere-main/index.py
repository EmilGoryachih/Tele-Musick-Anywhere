import telebot
from main import bot


def handler(event, _):  # Функция для переадресаци запросов в func Yandex Cloud
    message = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': '!',
    }
