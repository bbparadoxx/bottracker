import telebot
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,  CallbackQuery
from telebot_calendar import Calendar, CallbackData, ENGLISH_LANGUAGE
import DB
import settings
import visual
# import texts
# import time
# import multiprocessing
# import schedule

# bot = telebot.TeleBot(settings.TG_API_KEY)
bot = telebot.TeleBot(settings.TG_API_KEY_beta)

# calendar = Calendar(language=ENGLISH_LANGUAGE)
# calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")

#ручка, создающая файл под пользователя
@bot.message_handler(commands=["start"])
def start(message):
    user_data = [name: message.from_user.first_name,
                       None,
                       'x',
                       message.from_user.id]
    text = f'Привет, {message.from_user.first_name}!'
    # text += "Пожалуйста, укажи, который у тебя час. Формат: 09:13."
    bot.send_message(message.chat.id, text)
    # bot.register_next_step_handler(message, user_data.append(message))
    # # ИМЭЙЛ
    # # ПАРОЛЬ
    DB.create_user(user_data)
    text = f'Спасибо! Всё готово к работе:). Жми /track'
    bot.send_message(message.chat.id, text)



#разметка да-нет с привязкой по имени активности
def gen_markup(activity_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да", callback_data=f"cb_yes+{activity_name}"))
    markup.add(InlineKeyboardButton("Нет", callback_data=f"cb_no+{activity_name}"))
    return markup


#разметка да-ввод другого имени
def gen_markup_yes_input():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Да"))
    markup.add(KeyboardButton("Ввести другое имя"))
    return markup


#разметка да-нет на изменение конкретного трека
def gen_markup_change_track_date(activity_name, date):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    text1 = f"change_date_track_yes+{activity_name}+{date}"
    text2 = f"change_date_track_no+{activity_name}+{date}"
    markup.add(InlineKeyboardButton("Да", callback_data=text1))
    markup.add(InlineKeyboardButton("Нет", callback_data=text2))
    return markup


#разметка да-нет на удаление с привязкой по имени активности
def gen_markup_delete(activity_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да", callback_data=f"delete_yes+{activity_name}"))
    markup.add(InlineKeyboardButton("Нет", callback_data=f"delete_no+{activity_name}"))
    return markup


#разметка да-нет на удаление всех активностей
def gen_markup_delete_all():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да", callback_data="delete_all_yes"))
    markup.add(InlineKeyboardButton("Нет", callback_data="all_delete_no"))
    return markup


#разметка вариантов изменений
def gen_markup_change(activity_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Изменить или отменить отметку", callback_data=f"change_track+{activity_name}"))
    markup.add(InlineKeyboardButton("Переименовать активность", callback_data=f"change_name+{activity_name}"))
    return markup


#разметка полного списка активностей + предложение добавить активность
def gen_markup_activities(user_id):
    act_list = DB.get_activities_list(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(act_list) + 1
    for act in sorted(act_list):
        markup.add(InlineKeyboardButton(act, callback_data=act))
    markup.add(InlineKeyboardButton('Добавить новую активность', callback_data='new_activity'))
    return markup


#разметка полного списка активностей для показа
def gen_markup_activities_show(user_id):
    act_list = DB.get_activities_list(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(act_list) + 1
    for act in sorted(act_list):
        markup.add(InlineKeyboardButton(act, callback_data=f"show_act+{act}"))
    markup.add(InlineKeyboardButton('Все активности', callback_data='show_all'))
    return markup


#разметка полного списка активностей для изменения записи трека или названия активности
def gen_markup_activities_change(user_id):
    act_list = DB.get_activities_list(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(act_list) + 1
    for act in sorted(act_list):
        markup.add(InlineKeyboardButton(act, callback_data=f"change_act+{act}"))
    return markup


#разметка полного списка активностей для удаления
def gen_markup_activities_delete(user_id):
    act_list = DB.get_activities_list(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(act_list) + 1
    for act in sorted(act_list):
        markup.add(InlineKeyboardButton(act, callback_data=f"delete_act+{act}"))
    markup.add(InlineKeyboardButton('Все активности', callback_data='delete_all'))
    return markup


calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_track_change = CallbackData("calendar_track_change", "action", "year", "month", "day", "activity_name")


#разметка календаря с активностью
def show_calendar(call, activity_name):
    now = datetime.datetime.now()
    bot.send_message(
        call.from_user.id,
        f"Selected date for {activity_name}",
        reply_markup=calendar.create_calendar(
            name=f'{calendar_track_change.prefix}+{activity_name}',
            year=now.year,
            month=now.month,
        ),
    )

#разметка на выбор периода для всех активностей
def gen_markup_show_all_period():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton("Неделя", callback_data="show_week_all"))
    markup.add(InlineKeyboardButton("Месяц", callback_data="show_month_all"))
    markup.add(InlineKeyboardButton("Выбрать даты", callback_data="show_custom_all"))
    return markup



#убрать разметку
def delete_markup(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


#полный набор ответов на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # delete_markup(call)
    if "cb_yes" in call.data:
        DB.track_activity(call.from_user.id, call.data.split('+')[1], 1)
        bot.answer_callback_query(call.id, "Молодец!")
        show_this_week(call.from_user.id)
    elif "cb_no" in call.data:
        DB.track_activity(call.from_user.id, call.data.split('+')[1], 0)
        bot.answer_callback_query(call.id, "Бывает.")
    elif call.data == "new_activity":
        ask_for_activity_name(call.from_user.id)
    elif 'change_act' in call.data:
        text = f"Что вы хотите изменить в активности {call.data.split('+')[1]}?"
        bot.send_message(call.from_user.id, text, reply_markup=gen_markup_change(call.data.split('+')[1]))
    elif 'change_name' in call.data:
        ask_for_activity_rename(call.from_user.id, call.data.split('+')[1])
    elif 'change_track' in call.data:
        show_calendar(call, call.data.split('+')[1])
    elif call.data.startswith(calendar_track_change.prefix):
        name, action, year, month, day = call.data.split(calendar_track_change.sep)
        activity_name = name.split('+')[1]
        date = calendar.calendar_query_handler(
            bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
        if action == "DAY":
            date_change = date.strftime('%Y-%m-%d')
            if date <= datetime.datetime.today():
                score = DB.show_track(call.from_user.id, activity_name, date_change)
                text = f"Отметка активности {activity_name} за {date.strftime('%d.%m.%Y')}: {score}.\n'"
                text += "Хотите изменить?"
                bot.send_message(call.from_user.id, text,
                                 reply_markup=gen_markup_change_track_date(activity_name, date_change))
            else:
                bot.send_message(
                    chat_id=call.from_user.id,
                    text='Подожди, завтра еще не наступило. Будущее неизвестно.',
                    reply_markup=ReplyKeyboardRemove(),
                )
        elif action == "CANCEL":
            bot.send_message(
                chat_id=call.from_user.id,
                text='Отмена действия',
                reply_markup=ReplyKeyboardRemove(),
            )
    elif 'change_date_track_yes' in call.data:
        activity_name = call.data.split('+')[1]
        date = call.data.split('+')[2]
        ask_for_change_activity_date_track(call.from_user.id, activity_name, date)
    elif 'change_date_track_no' in call.data:
        bot.answer_callback_query(call.id, "Бывает.")
    elif call.data == "show_all":
        text = "За какой период показать данные?"
        bot.send_message(call.from_user.id, text, reply_markup=gen_markup_show_all_period())
    elif call.data == "show_week_all":
        show_this_week(call.from_user.id)
    elif call.data == "show_month_all":
        show_this_month(call.from_user.id)
    elif call.data == "show_custom_all":
        text = "Здесь скоро что-то будет:)"
        bot.send_message(call.from_user.id, text)
    elif 'show_act' in call.data:
        text = DB.count_track_relation(call.from_user.id, call.data.split('+')[1])
        bot.send_message(call.from_user.id, text)
    elif "delete_yes" in call.data:
        activity = call.data.split('+')[1]
        DB.delete_activity(call.from_user.id, activity)
        bot.answer_callback_query(call.id, f"Активность {activity} удалена")
    elif "delete_no" in call.data:
        text = 'Может пригодиться, хорошо, что передумал'
        bot.send_message(call.from_user.id, text)
    elif call.data == "delete_all_yes":
        DB.delete_all_activities(call.from_user.id)
        bot.answer_callback_query(call.id, "Все активности удалены")
    elif call.data == "delete_all":
        text = f"Точно хочешь удалить отметки по всем своим активностям?"
        bot.send_message(call.from_user.id, text, reply_markup=gen_markup_delete_all())
    elif 'delete_act' in call.data:
        text = f"Точно хочешь удалить отметки по активности '{call.data.split('+')[1]}'?"
        bot.send_message(call.from_user.id, text, reply_markup=gen_markup_delete(call.data.split('+')[1]))
    else:
        ask_for_activity(call.from_user.id, call.data)


# функция, собирающая название активности
def ask_for_activity_name(user_id):
    text = 'Введи название активности'
    bot.send_message(user_id, text, reply_markup=ReplyKeyboardRemove())
    DB.set_current_status(user_id, 'asking_new_activity_name')


# функция, собирающая название активности для переименования
def ask_for_activity_rename(user_id, activity_name):
    text = 'Введи новое название активности'
    bot.send_message(user_id, text, reply_markup=ReplyKeyboardRemove())
    DB.set_current_status(user_id, 'asking_activity_rename')
    DB.set_current_activity(user_id, activity_name)


# функция, собирающая название активности и дату для изменения трэка
def ask_for_change_activity_date_track(user_id, activity_name, date):
    text = f'Введи новую отметку активности {activity_name} за {date}'
    bot.send_message(user_id, text, reply_markup=ReplyKeyboardRemove())
    DB.set_current_status(user_id, 'asking_change_activity_date_track')
    DB.set_current_activity(user_id, activity_name)
    DB.set_current_date_for_change(user_id, date)


# функция, предлагающая трэкнуть активность
def ask_for_activity(user_id, activity_name):
    text = f'Выполнил {activity_name}?'
    bot.send_message(user_id, text, reply_markup=gen_markup(activity_name))


# функция, предлагающая трэкнуть активность
def show_this_week(user_id):
    week = datetime.datetime.today().isocalendar()[1]
    year = datetime.datetime.today().isocalendar()[0]
    start_date = datetime.datetime.fromisocalendar(year, week, 1)
    end_date = datetime.datetime.fromisocalendar(year, week, 7)
    pic = visual.create_activities_img(*DB.collect_all_data_toshow(user_id, start_date, end_date))
    bot.send_photo(user_id, open(f'{pic}', 'rb'))


# функция, предлагающая трэкнуть активность
def show_this_month(user_id):
        year = datetime.date.today().strftime('%Y-%m-%d').split('-')[0]
        month = datetime.date.today().strftime('%Y-%m-%d').split('-')[1]
        if int(month) in (1, 3, 5, 7, 8, 10, 12):
            end_date = datetime.datetime.strptime(f'{year}-{month}-31', '%Y-%m-%d')
        elif int(month) in (4, 6, 9, 11):
            end_date = datetime.datetime.strptime(f'{year}-{month}-30', '%Y-%m-%d')
        elif int(year) % 4 == 0:
            end_date = datetime.datetime.strptime(f'{year}-{month}-29', '%Y-%m-%d')
        else:
            end_date = datetime.datetime.strptime(f'{year}-{month}-28', '%Y-%m-%d')
        start_date = datetime.datetime.strptime(f'{year}-{month}-1', '%Y-%m-%d')
        pic = visual.create_activities_img(*DB.collect_all_data_toshow(user_id, start_date, end_date))
        bot.send_photo(user_id, open(f'{pic}', 'rb'))


#ручка создания новой активности
@bot.message_handler(commands=["add"])
def add_activity(message):
    ask_for_activity_name(message.from_user.id)


#ручка трэка
@bot.message_handler(commands=["track"])
def track(message):
    text = 'Какую активность ты будешь трекать?'
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_activities(message.from_user.id))


#ручка показов
@bot.message_handler(commands=["show"])
def show_stats(message):
    text = "За какой период показать данные?"
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_show_all_period())


#ручка показов
@bot.message_handler(commands=["show_unique"])
def show_stats_unique(message):
    text = 'Какую активность показать?'
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_activities_show(message.from_user.id))


#ручка изменений
@bot.message_handler(commands=["change"])
def change_stats(message):
    text = 'Какую активность хотите изменить?'
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_activities_change(message.from_user.id))


#ручка удаления
@bot.message_handler(commands=["delete"])
def delete(message):
    text = 'Выбери активность, которую хочешь удалить'
    bot.send_message(message.chat.id, text, reply_markup=gen_markup_activities_delete(message.from_user.id))


#Основной диалог с треком  (запускается после старта)
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    status = DB.get_user_status(message.from_user.id)
    if status == "asking_new_activity_name":
        activity_name = message.text
        if DB.check_activity(message.from_user.id, activity_name):
            text = f'Активность {activity_name} уже есть, не могу её создать.\n'
            text += f'Чтобы создать новую активность или отметить активность {activity_name}, жми /track'
            bot.send_message(message.chat.id, text)
            DB.set_current_status(message.from_user.id, '')
        else:
            text = f"Вы хотите создать активность с именем '{activity_name}'?"
            DB.set_current_status(message.from_user.id, 'asking_activity_name_is_true')
            DB.set_current_activity(message.from_user.id, activity_name)
            bot.send_message(message.chat.id, text, reply_markup=gen_markup_yes_input()) # клавиатура "Да" или "Ввести другое имя"
    elif status == 'asking_activity_name_is_true':
        if message.text == 'Да':
            # создаём активность и удаляем клавиатуру
            activity_name = DB.get_user_current_activity(message.from_user.id)
            DB.add_activity(message.from_user.id, activity_name)
            DB.set_current_status(message.from_user.id, '')
            DB.set_current_activity(message.from_user.id, '')
            text = f'Активность {activity_name} добавлена!'
            bot.send_message(message.chat.id, text, reply_markup=ReplyKeyboardRemove())
        elif message.text == 'Ввести другое имя':
            ask_for_activity_name(message.from_user.id)
        else:
            bot.send_message(message.chat.id, "Жми на кнопку", reply_markup=gen_markup_yes_input())
    elif status == "asking_activity_rename":
        new_name = message.text
        if DB.check_activity(message.from_user.id, new_name):
            text = f'Активность {new_name} уже есть, нельзя использовать это имя.\n'
            text += 'Чтобы поменять имя активности, жми /change'
            bot.send_message(message.chat.id, text)
            DB.set_current_status(message.from_user.id, '')
        else:
            old_name = DB.get_user_current_activity(message.from_user.id)
            DB.rename_activity(message.from_user.id, new_name, old_name)
            DB.set_current_status(message.from_user.id, '')
            DB.set_current_activity(message.from_user.id, '')
            text = f'Активность {old_name} переименована в {new_name}!'
            bot.send_message(message.chat.id, text)
    elif status == "asking_change_activity_date_track":
        new_score = int(message.text)
        activity_name = DB.get_user_current_activity(message.from_user.id)
        date = DB.get_user_date_for_change(message.from_user.id)
        DB.change_track(new_score, message.from_user.id, activity_name, date)
        DB.set_current_status(message.from_user.id, '')
        DB.set_current_activity(message.from_user.id, '')
        DB.set_current_date_for_change(message.from_user.id, '')
        text = f'Отметка активности {activity_name} за {date} теперь {new_score}.'
        bot.send_message(message.chat.id, text)


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

