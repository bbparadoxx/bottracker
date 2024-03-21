import settings
import telebot
import markups
import DB


bot = telebot.TeleBot(settings.TG_API_KEY_beta)


def main() -> None:
    bot.enable_save_next_step_handlers()
    bot.load_next_step_handlers()
    print('Бот успешно запустился!')
    bot.infinity_polling()


@bot.message_handler(commands=["start"])
def start(message):
    if DB.is_user_in_db(message.from_user.id):
        bot.send_message(message.chat.id, 'Привет!')
    else:
        text = f'Спасибо! Всё готово к работе :) Выбирайте свой часовой пояс'
        bot.send_message(message.chat.id, text, reply_markup=markups.gen_utc_markup())


@bot.message_handler(commands=["create_activity"])
def create_activity(message):
    text = 'Введи имя активности'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, process_enter_activity_name_step)


@bot.message_handler(commands=["create_checklist"])
def create_checklist(message):
    user_id = DB.get_user_id(message.from_user.id)
    text = 'Выбери чеклист, который хочешь изменить, или выбери создать чеклист'
    cur_markup = markups.gen_checklists_markup(user_id)
    bot.send_message(message.chat.id, text, reply_markup=cur_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    delete_markup(call)
    if call.data == 'add_checklist':
        msg = bot.send_message(call.from_user.id, 'Введи имя нового чеклиста')
        bot.register_next_step_handler(msg, process_enter_checklist_name_step)
    elif call.data.startswith('UTC'):
        bot.send_message(call.from_user.id, f'Вы выбрали: {call.data}')
        h, m = map(int, call.data.replace('UTC', '').split(':'))
        minutes = h * 60 + (m if h > 0 else -m)
        DB.create_user({'telegram_id': call.from_user.id, 'UTC': minutes})
        DB.create_main_checklist(DB.get_user_id(call.from_user.id))
        bot.send_message(call.from_user.id, f'Учётная запись создана. Жми /checklists')
    elif call.data.startswith('choose_checklist_'):
        checklist_name = call.data[len('choose_checklist_'):]
        txt = f'Чеклист {checklist_name} выбран!'
        bot.send_message(call.from_user.id, txt)
        user_id = DB.get_user_id(call.from_user.id)
        checklist_id = DB.get_checklist_id(user_id, checklist_name)
        show_activities_markup(call.from_user.id, checklist_id)
    elif call.data.startswith('measure_bool_'):
        user_id = DB.get_user_id(call.from_user.id)
        activity_name = call.data[len('measure_bool_'):]
        DB.create_activity(user_id, activity_name, True, '-')
        tel_id = call.from_user.id
        act_id = DB.get_activity_id(user_id, activity_name)
        check_other_checklists(user_id, tel_id, act_id)
    elif call.data.startswith('measure_physics_'):
        text = 'В чём будешь измерять активность? Например, км, шаги, литры.'
        msg = bot.send_message(call.from_user.id, text)
        activity_name = call.data[len('measure_physics_'):]
        tel_id = call.from_user.id
        bot.register_next_step_handler(msg, process_measurement, activity_name, tel_id)
    elif call.data.startswith('activity_to_checklists_'):
        act_id = int(call.data.split('_')[3])
        check_id = int(call.data.split('_')[4])
        DB.change_act_checklist_connection(act_id, check_id)
        tel_id = call.from_user.id
        user_id = DB.get_user_id(call.from_user.id)
        txt = 'Хочешь добавить активность в какой-нибудь чеклист?'
        cur_markup = markups.gen_other_checklists_markup(user_id, act_id)
        bot.send_message(tel_id, txt, reply_markup=cur_markup)
    elif call.data.startswith('activities_to_checklist_'):
        act_id = int(call.data.split('_')[3])
        check_id = int(call.data.split('_')[4])
        DB.change_act_checklist_connection(act_id, check_id)
        tel_id = call.from_user.id
        user_id = DB.get_user_id(call.from_user.id)
        txt = (
            'Выбери существующие активности, которые хочешь добавить в чеклист. '
            'Создать новые можно будет позже.'
        )
        cur_markup = markups.gen_add_activities_to_checklist_markup(user_id, check_id)
        bot.send_message(tel_id, txt, reply_markup=cur_markup)
    elif call.data == 'accept_activities':
        txt = f'Активность успешно добавлена в чеклисты!'
        bot.send_message(call.from_user.id, txt)


def process_enter_checklist_name_step(message):
    checklist_name = message.text.strip()
    user_id = DB.get_user_id(message.from_user.id)
    if DB.is_checklist_in_db(user_id, checklist_name):
        txt = f'Чеклист {checklist_name} уже есть. Введи другое имя.'
        msg = bot.send_message(message.from_user.id, txt)
        bot.register_next_step_handler(msg, process_enter_checklist_name_step)
    else:
        checklist_id = DB.create_checklist(user_id, checklist_name)
        txt = f'Чеклист {checklist_name} создан успешно!'
        bot.send_message(message.from_user.id, txt)
        show_activities_markup(message.from_user.id, checklist_id)


def process_measurement(message, activity_name, tel_id):
    measurement = message.text.strip()
    user_id = DB.get_user_id(message.from_user.id)
    DB.create_activity(user_id, activity_name, False, measurement)
    act_id = DB.get_activity_id(user_id, activity_name)
    check_other_checklists(user_id, tel_id, act_id)


def check_other_checklists(user_id, tel_id, act_id):
    lst = DB.get_checklists_except_main(user_id)
    if lst:
        txt = 'Хочешь добавить активность в какой-нибудь чеклист? Выбери все!'
        cur_markup = markups.gen_other_checklists_markup(user_id, act_id)
        bot.send_message(tel_id, txt, reply_markup=cur_markup)
    else:
        txt = 'Активность успешно добавлена!'
        bot.send_message(tel_id, txt)


def show_activities_markup(tg_id, checklist_id):
    user_id = DB.get_user_id(tg_id)
    cur_markup = markups.gen_add_activities_to_checklist_markup(user_id, checklist_id)
    txt = (
        'Выбери существующие активности, которые хочешь добавить в чеклист. '
        'Создать новые можно будет позже.'
    )
    bot.send_message(tg_id, txt, reply_markup=cur_markup)


def process_enter_activity_name_step(message):
    activity_name = message.text.strip()
    user_id = DB.get_user_id(message.from_user.id)
    if DB.is_activity_in_db(user_id, activity_name):
        txt = f'Активность {activity_name} уже есть. Введи другое имя.'
        msg = bot.send_message(message.from_user.id, txt)
        bot.register_next_step_handler(msg, process_enter_activity_name_step)
    else:
        text = f"Как измеряется активность '{activity_name}':сделано/не сделано или физическая величина (км)?"
        cur_markup = markups.gen_activity_measure_markup(activity_name)
        bot.send_message(message.chat.id, text, reply_markup=cur_markup)


def delete_markup(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


if __name__ == '__main__':
    main()
