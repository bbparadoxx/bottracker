import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# import time
# import multiprocessing
# import schedule

import DB
import settings


bot = telebot.TeleBot(settings.TG_API_KEY)


#ручка, создающая файл под пользователя
@bot.message_handler(commands=["start"])
def start(message):
    DB.create_user(message.from_user.id)
    text = f'Я на связи, {message.from_user.first_name}. Жми /track'
    bot.send_message(message.chat.id, text)

#ручка показов
@bot.message_handler(commands=["show_stats"])
def show_stats(message):
    bot.send_message(message.chat.id, DB.count_track_abs(message.from_user.id))
    bot.send_message(message.chat.id, DB.count_track_relation(message.from_user.id))


#разметка да-нет с привязкой по имени активности
def gen_markup(activity_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data=f"cb_yes+{activity_name}"))
    markup.add(InlineKeyboardButton("No", callback_data=f"cb_no+{activity_name}"))
    return markup


#разметка полного списка активностей + предложение добавить активность
def gen_markup_activities(user_id):
    act_list = DB.get_activities_list(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(act_list)
    for act in sorted(act_list):
        markup.add(InlineKeyboardButton(act, callback_data=act))
    markup.add(InlineKeyboardButton('Добавить новую активность', callback_data='new_activity'))
    return markup


#полный набор ответов на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "cb_yes" in call.data:
        DB.track_activity(call.from_user.id, call.data.split('+')[1], 1)
        bot.answer_callback_query(call.id, "Молодец!")
    elif "cb_no" in call.data:
        DB.track_activity(call.from_user.id, call.data.split('+')[1], 0)
        bot.answer_callback_query(call.id, "Бывает.")
    elif call.data == "new_activity":
        ask_for_activity_name(call.from_user.id)
    else:
        ask_for_activity(call.from_user.id, call.data)


#создать новую активность по /create_activity


#функция, собирающая название активности
def ask_for_activity_name(user_id):
    text = 'Введи название активности'
    bot.send_message(user_id, text)
    DB.set_current_status('asking_new_activity_name')


def ask_for_activity(user_id, activity_name):
    text = f'делаль {activity_name}?'
    bot.send_message(user_id, text, reply_markup=gen_markup(activity_name))


@bot.message_handler(commands=["track"])
def track(message):
    text = 'Какую активность ты будешь трекать?'
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_activities(message.from_user.id))


#Основной диалог с треком  (запускается после старта)
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    state = DB.get_user_status(message.from_user.id)
    if state == "asking_new_activity_name":
        activity_name = message.text
        if DB.check_activity(activity_name):
            text = f'Активность {activity_name} уже есть, не могу её создать.\n'
            text += f'Чтобы создать новую активность или отметить активность {activity_name}, жми /track'
            bot.send_message(message.chat.id, text)
            DB.set_current_status('')
        else:
            text = f"Вы хотите создать активность с именем '{activity_name}'?"
            DB.set_current_status('asking_activity_name_is_true')
            DB.set_current_activity(activity_name)
            bot.send_message(message.chat.id, text) # клавиатура "Да" или "Ввести другое имя"
    elif state == 'asking_activity_name_is_true':
        if message.text == 'Да':
            # создаём активность и удаляем клавиатуру
            activity_name = DB.get_user_current_activity()
            DB.add_activity(activity_name)
            DB.set_current_status('')
            DB.set_current_activity('')
            text = f'Активность {activity_name} добавлена!'
            bot.send_message(message.chat.id, text)
        elif message.text == 'Ввести другое имя':
            # кидаем на шаг ввода имени
            pass
        else:
            pass
            # говорим жми на кнопку


if __name__ == '__main__':
    print('Бот успешно запустился!')
    # start_process()
    bot.polling(none_stop=True, interval=0)


#Невошедшие приколы

#1
# def start_asking_for_track():
#     text = f"Занимался сегодня активностью?"
#     for user_id in DB.get_user_ids():
#         bot.send_message(user_id, text, reply_markup=gen_markup())


#2. Шедулер
# def start_process():  # Запуск Process
#     multiprocessing.Process(target=start_schedule, args=()).start()
#
#
# def start_schedule():
#     schedule.every().day.at("17:43").do(start_asking_for_track)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
