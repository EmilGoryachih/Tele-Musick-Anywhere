import os
from difflib import SequenceMatcher
import re
import string

import requests
import telebot
from telebot import types

from data import db_session
from data.songs import Song
from data.profile import Users
from image_ot_qr import QR_Operation
from speech import Recognition

db_session.global_init("db/musik.db")  # подключаем сессию sqlalchemy
URL = "https://api.telegram.org/bot"
with open("keys/apikey") as f:
    __APIKEY__ = f.readline()
with open("keys/paykey") as f:
    __PAYKEY__ = f.readline()
bot = telebot.TeleBot(__APIKEY__)

users_step = {}
CAN_ADD = False
# словарь статусов пользователей (некий аналог динамического json файла)
find_musick = types.KeyboardButton("Найти музыку")
add_musick = types.KeyboardButton("Добавить музыку")
other = types.KeyboardButton("Еще")
user = types.KeyboardButton("Профиль")
profile_statistic = types.KeyboardButton("Статистика")
adv = types.KeyboardButton("Реклама")
text = types.KeyboardButton("Текст")
voice = types.KeyboardButton("Голос")
yes = types.KeyboardButton("Да")
eng = types.KeyboardButton("Английский")
rus = types.KeyboardButton("Русский")
back_button = types.KeyboardButton("Назад")
qr_button = types.KeyboardButton("QR код")
share = types.KeyboardButton("Поделиться")
playlist = types.KeyboardButton("Плейлист")
add_to_playlist = types.KeyboardButton("Добавить в плейлист")


# такая строка отвечает за тип обрабатывваемых


@bot.message_handler(content_types=["text",
                                    "start"])
# соосбщений(эта за текст и команду старт)
def main(message):
    global CAN_ADD

    if not message.from_user.id in users_step:  # проверка на присутсвие в словаре
        users_step[message.from_user.id] = "home"
        db_sess = db_session.create_session()
        user_table = db_sess.query(Users).filter(
            Users.user_id == message.from_user.id).first()  # проверяем наличие пользователя в бд

        if user_table is None:
            user_table = Users()
            # устанавливаем базовые значения
            user_table.user_id = message.chat.id
            user_table.listen_statistic = '0'
            user_table.add_statistic = '0'
            user_table.ads_statistic = '0'
            db_sess.add(user_table)
            db_sess.commit()

    if message.text == "/start" or message.text == "Назад":  # выход домой (если нажали старт или назад)

        users_step[message.from_user.id] = "home"  # меняем местонахождение пользователя в словаре

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # стиль кнопок
        markup.add(find_musick, add_musick, other, playlist)  # добавляем кнопки
        bot.send_message(message.chat.id,  # отправлем сообщение
                         text="Привет, {0.first_name}! Я тестируюсь".format(message.from_user), reply_markup=markup)
        # все последующие сточки делают тоже-самое, отличаясь кнопками и местоположением пользователя

    elif message.text == "Еще":

        users_step[message.from_user.id] = "other"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button, user, adv)
        bot.send_message(message.chat.id, text="Дополнительные функции", reply_markup=markup)

    elif message.text == "Реклама":
        users_step[message.from_user.id] = "schearch_for_adv"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id, text="Напишите название песни", reply_markup=markup)

    elif message.text == "Профиль":
        users_step[message.from_user.id] = "user"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(profile_statistic, back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Добро пожаловать в ваш профиль".format(
                             message.from_user), reply_markup=markup)

    elif message.text == "Статистика":

        users_step[message.from_user.id] = "profile_statistic"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Предоставляю вашу статистику:".format(
                             message.from_user), reply_markup=markup)

        db_sess = db_session.create_session()
        user_table = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
        make_photo = QR_Operation()
        make_photo.statistic_image(user_table.user_id, user_table.listen_statistic, user_table.add_statistic,
                                   user_table.ads_statistic)
        # рисуем статистику пользователя на специальном фоне

        bot.send_photo(message.chat.id, open(f"pass/statistic-{user_table.user_id}.jpg", "rb"))
        # отправляем статистику

        os.remove(f"pass/statistic-{user_table.user_id}.jpg")
        # удаляем ненужные файлы

    elif message.text == "Добавить музыку":

        users_step[message.from_user.id] = "musick_add"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Скинь сначала название, текст(можно самую узнаваемую часть), затем "
                              "фото и потом аудио в виде файла и дождитесь ответа бота".format(
                             message.from_user), reply_markup=markup)

    elif message.text == "Найти музыку":

        CAN_ADD = True
        users_step[message.from_user.id] = "musick_find"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(text)
        markup.row(qr_button, voice)
        markup.row(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Выбери формат поиска".format(message.from_user), reply_markup=markup)

    elif message.text == "Текст":

        users_step[message.from_user.id] = "text"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Напиши название или часть текста песни".format(
                             message.from_user),
                         reply_markup=markup)

    elif message.text == "Голос":

        users_step[message.from_user.id] = "voice"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button, rus, eng)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, выбери язык".format(
                             message.from_user),
                         reply_markup=markup)

    elif message.text == "QR код":

        users_step[message.from_user.id] = "qr"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, жду qr код".format(message.from_user),
                         reply_markup=markup)

    elif message.text == "Поделиться":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        db_sess = db_session.create_session()
        result = db_sess.query(Song.qr).filter(Song.name == users_step[message.from_user.id]).first()
        bot.send_photo(message.chat.id, open(result[0], "rb"))

    elif message.text == "Плейлист":  # изменить
        db_sess = db_session.create_session()
        result = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
        if result:
            for _ in result.user_playlist.split(',')[:-1]:
                music_link = db_sess.query(Song.song).filter(Song.id == str(_)).first()
                print(music_link)
                bot.send_audio(message.from_user.id, music_link[0])
        else:
            bot.send_message('Ваш плейлист пуст')

    elif message.text == "Добавить в плейлист":  # изменить
        if CAN_ADD:
            db_sess = db_session.create_session()
            music_id = db_sess.query(Song.id).filter(Song.name == users_step[message.from_user.id]).first()
            user_table = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
            print(user_table.user_playlist)
            if user_table.user_playlist is None:
                user_table.user_playlist = ('')
            if str(music_id[0]) not in user_table.user_playlist:
                user_table.user_playlist = (user_table.user_playlist + str(music_id[0]) + ',')
                bot.send_message(message.chat.id, 'Песня добавлена в плейлист')
            else:
                bot.send_message(message.chat.id, 'Эта песня уже есть в плейлисте')
            db_sess.commit()
            CAN_ADD = False

    elif message.text in ("Русский", "Английский") and users_step[
        message.from_user.id] == "voice":  # Запуск поиска по тексту
        if message.text == "Русский":
            users_step[message.from_user.id] = "ru_RU"
        else:
            users_step[message.from_user.id] = "eng_ENG"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, жду голосовое сообщение".format(message.from_user),
                         reply_markup=markup)

    elif users_step[message.from_user.id] == "text":  # Запуск поиска по тексту
        send_message(message.chat.id, message.text, message)

    elif users_step[message.from_user.id] == "schearch_for_adv":  # Запуск поиска по тексту
        db_sess = db_session.create_session()
        result = list(db_sess.query(Song.photo, Song.song, Song.name).filter(Song.name == message.text).distinct())
        if result:
            users_step[message.from_user.id] = ["check_for_adv"] + list(result[0])
            result = result[0]
            requests.get(f'{URL}{__APIKEY__}/sendPhoto?chat_id={message.chat.id}&photo={result[0]}&caption={result[2]}')
            requests.get(f"{URL}{__APIKEY__}/sendAudio?chat_id={message.chat.id}&audio={result[1]}")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(back_button, yes)
            bot.send_message(message.chat.id,
                             text="{0.first_name}, это то что нужно?".format(message.from_user),
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id,  # оно работает, осталось сделать поиск по таблице
                             text="Извините, ничего не нашлось")

    elif users_step[message.from_user.id][0] == "check_for_adv" and (message.text == "Да"):
        musik_adv = types.LabeledPrice(label='Реклама песни', amount=10000)
        if __PAYKEY__.split(':')[1] == 'TEST':
            bot.send_invoice(message.chat.id, title="Оплата", description=f"Реклама среди пользователей",
                             provider_token=__PAYKEY__, currency="rub",
                             is_flexible=False,
                             prices=[musik_adv, ],
                             start_parameter='payment-test', invoice_payload="payload-test"
                             )

    elif users_step[message.from_user.id] == "musick_add":  # статус когда пользователь добавил название песни
        users_step[message.from_user.id] = ["musick_add-text", message.text]

    elif users_step[message.from_user.id][0] == "musick_add-text":  # статус когда пользователь добавил название песни
        users_step[message.from_user.id].append(message.text)
        users_step[message.from_user.id][0] = "musick_add-image"

    print(users_step)


@bot.message_handler(content_types=['voice'])
def get_voice(message):
    if users_step[message.from_user.id] in ("ru_RU", "eng_ENG"):
        file_info = bot.get_file(message.voice.file_id)
        path = file_info.file_path
        file_name = "pass/" + os.path.basename(path)
        print(file_name)
        doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(__APIKEY__, file_info.file_path))
        with open(file_name, 'wb') as file:
            file.write(doc.content)
        x = Recognition(file_name, users_step[message.from_user.id])
        result = x.get_audio_messages()
        if result:
            send_message(message.chat.id, result, message)
        else:
            bot.send_message(message.chat.id, 'Не смог распознать текст')


@bot.pre_checkout_query_handler(func=lambda query: True)  # функция проверки прихода оплаты
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])  # при успешной оплате
def payed(message):
    bot.send_message(message.chat.id, "Спасибо за покупку")
    db_sess = db_session.create_session()
    result = list(db_sess.query(Users.user_id).distinct())[0]
    names = users_step[message.from_user.id][1:]
    for i in result:
        requests.get(f'{URL}{__APIKEY__}/sendPhoto?chat_id={i}&photo={names[0]}&caption=Спонсорская песня: {names[2]}')
        requests.get(f"{URL}{__APIKEY__}/sendAudio?chat_id={i}&audio={names[1]}")


@bot.message_handler(content_types=['photo'])  # тут при отправке фото (не файл)
def image(message):
    if message.from_user.id in users_step:
        print(users_step[message.from_user.id][0])
        # проверка на нахождение в нужом шаге, иначе могут сломать отправив фото в неположеном месте
        if users_step[message.from_user.id][0] == "musick_add-image":
            file_photo_id = message.photo[-1].file_id  # достаем id фото
            users_step[message.from_user.id].append(str(file_photo_id))  # добавляем рядом с шагом
            users_step[message.from_user.id][0] = "musick_add-file"  # и ставим следющий шаг
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)  # получаем файл
            downloaded_file = bot.download_file(file_info.file_path)  # скачиваем его
            src = 'pass/' + file_photo_id + ".png"  # даём имя
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)  # записываем
        elif users_step[message.from_user.id] == "qr":  # тестовое условие декода qr
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'pass/' + message.photo[1].file_id + ".png"
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            dec = QR_Operation("pass/" + message.photo[1].file_id)
            text_qr = dec.qr_decode()
            os.remove("pass/" + message.photo[1].file_id + ".png")
            db_sess = db_session.create_session()
            if text_qr.isdigit():
                result = list(db_sess.query(Song.gif, Song.song, Song.name).filter(Song.id == int(text_qr)).distinct())
            else:
                result = False
            if result:
                result = result[0]
                bot.send_message(message.chat.id,
                                 text=result[2].format(
                                     message.from_user))
                bot.send_animation(message.chat.id, open(result[0], 'rb'))
                requests.get(f"{URL}{__APIKEY__}/sendAudio?chat_id={message.chat.id}&audio={result[1]}")
            else:
                bot.send_message(message.chat.id,  # оно работает, осталось сделать поиск по таблице
                                 text="Извините, ничего не нашлось")


@bot.message_handler(content_types=['audio'])  # при отправке аудио (файл)
def doc(message):
    if message.from_user.id in users_step:
        if users_step[message.from_user.id][0] == "musick_add-file":
            file = str(message.audio.file_id)
            mus = Song()  # тут добавление в таблцу происходит
            mus.name = users_step[message.from_user.id][1]  # подробнее смотрите в файле с классом
            mus.photo = users_step[message.from_user.id][3]

            first_directory = os.getcwd()
            os.chdir('gif')
            gif_in_directory = os.listdir()
            if len(gif_in_directory) == 0:
                song_id = '1'
            else:
                gif_in_directory = ' '.join('  '.join(gif_in_directory).split('\n'))
                gif_in_directory = sorted(gif_in_directory.split(),
                                          key=lambda x: int(re.sub(r'.*?(\d+).*', r'\1', x + '_99999')))
                song_id = str(int(gif_in_directory[-1].split('-')[1].split('.')[0]) + 1)  # ищем индекс последней песни
            os.chdir(first_directory)

            image_creator = QR_Operation(f'qr-{song_id}')

            image_creator.make_gif(f'name-{song_id}', f'{users_step[message.from_user.id][-1]}')  # создаём гиф с диском
            print(f'name-{song_id}', f'{users_step[message.from_user.id][-1]}')
            image_creator.qr_coder(song_id)  # делаем базовый qr
            image_creator.im_to_qr(f'pass/{users_step[message.from_user.id][-1]}')  # кастомизируем его
            os.remove(f'pass/qr-{song_id}-base.png')

            mus.gif = f'gif/name-{song_id}.gif'
            mus.qr = f"qr/qr-{song_id}.png"
            mus.song = file
            tet = users_step[message.from_user.id][2]
            tt = str.maketrans(dict.fromkeys(string.punctuation))
            mus.text = ' '.join(re.split("—|–|\n", tet.translate(tt).lower()))
            mus.author = message.from_user.id

            db_sess = db_session.create_session()  # собственно сессия
            db_sess.add(mus)  # вначале добавляем в сессию
            db_sess.commit()  # потом комитим обязательно

            muss = db_sess.query(Song).filter(Users.user_id == message.from_user.id).first()
            muss.audio_location = str(file_name)
            user_table = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
            user_table.add_statistic = str(int(user_table.add_statistic) + 1)
            db_sess.commit()
            bot.send_message(message.chat.id,
                             text="Успешно добавлено")


def send_message(chat_id, name, message):  # функция отправки нормального сообщения с песней
    db_sess = db_session.create_session()  # обязательно сессия для запросов

    result = list(
        db_sess.query(Song.gif, Song.song).filter(str(Song.name) == name).distinct())  # запрос поиска по названи

    if result:  # если нашли имя
        result = result[0]  # тут был список с кортежем
        users_step[message.from_user.id] = name.lower()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button, share, add_to_playlist)
        bot.send_message(message.chat.id,
                         text=name.format(
                             message.from_user), reply_markup=markup)
        bot.send_animation(message.chat.id, open(result[0], 'rb'))
        requests.get(f"{URL}{__APIKEY__}/sendAudio?chat_id={chat_id}&audio={result[1]}")
        db_sess = db_session.create_session()
        user_table = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
        user_table.add_statistic += str(int(user_table.add_statistic) + 1)
        db_sess.commit()
    else:
        songg = db_sess.execute(f"""SELECT * FROM songs
                WHERE text LIKE '%{name.lower()}%' """).first()  # изменить
        try:
            result = list(db_sess.query(Song.gif, Song.song, Song.name).filter(
                Song.id == songg[0]).distinct())  # и ищем оставшееся по тексту'''
        except:
            pass

        if result:
            result = result[0]
            users_step[message.from_user.id] = result[2]
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(back_button, share, add_to_playlist)
            bot.send_message(message.chat.id,
                             text=f"{result[2]}", reply_markup=markup)
            bot.send_animation(message.chat.id, open(result[0], 'rb'))
            requests.get(f"{URL}{__APIKEY__}/sendAudio?chat_id={chat_id}&audio={result[1]}")
            db_sess = db_session.create_session()
            user_table = db_sess.query(Users).filter(Users.user_id == message.from_user.id).first()
            user_table.add_statistic = str(int(user_table.add_statistic) + 1)
            db_sess.commit()
        else:
            bot.send_message(message.chat.id,
                             text="Ничего не нашлось... Добавь эту песню нам в коллекцию")  # ну тут понятно по контексту, если ничего ненашли


def run():
    bot.polling(none_stop=True, interval=1)  # это запускает и обновляем бота


if __name__ == "__main__":
    run()
