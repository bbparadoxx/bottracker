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
        user = DB.create_user({'telegram_id': call.from_user.id, 'UTC': minutes})
        bot.send_message(call.from_user.id, f'Учётная запись создана. Жми /checklists')
    elif call.data.startswith('choose_checklist_'):
        checklist_name = call.data[len('choose_checklist_'):]
        txt = f'Чеклист {checklist_name} выбран!'
        msg = bot.send_message(call.from_user.id, txt)
        user_id = DB.get_user_id(call.from_user.id)
        checklist_id = DB.get_checklist_id(user_id, checklist_name)
        set_activities_to_checklist(call.from_user.id, checklist_id)


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
        msg = bot.send_message(message.from_user.id, txt)
        set_activities_to_checklist(message.from_user.id, checklist_id)


def set_activities_to_checklist(tg_id, checklist_id):
    user_id = DB.get_user_id(tg_id)
    cur_markup = markups.gen_add_activities_to_checklist_markup(user_id, checklist_id)
    txt = (
        'Выбери существующие активности, которые хочешь добавить в чеклист. '
        'Создать новые можно будет позже.'
    )
    msg = bot.send_message(tg_id, txt, reply_markup=cur_markup)


def delete_markup(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


if __name__ == '__main__':
    main()
