from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import DB

def gen_utc_markup():
    markup = InlineKeyboardMarkup()
    for callback_data, text in dict_UTC:
        markup.add(InlineKeyboardButton(text, callback_data='UTC' + callback_data))
    return markup


def gen_checklists_markup(user_id):
    checklists = DB.get_checklists(user_id)
    markup = InlineKeyboardMarkup()
    for checklist_name in checklists:
        markup.add(InlineKeyboardButton(checklist_name, callback_data=f"choose_checklist_{checklist_name}"))
    markup.add(InlineKeyboardButton('Создать чеклист', callback_data='add_checklist'))
    return markup


def gen_add_activities_to_checklist_markup(user_id, checklist_id):
    activities = DB.get_activities(user_id)
    markup = InlineKeyboardMarkup()
    for act_id, name, creation_date, owner, is_bool, measurement in activities:
        activity_name = '✔ ' if DB.is_activity_in_checklist(act_id, checklist_id) else '❌ '
        activity_name += name
        callback_data = f'activities_to_checklist_{act_id}_{checklist_id}'
        markup.add(
            InlineKeyboardButton(activity_name, callback_data=callback_data)
        )
    markup.add(InlineKeyboardButton('Подтвердить выбор', callback_data='accept_activities'))
    return markup


def gen_other_checklists_markup(user_id, act_id):
    checklists = DB.get_checklists_except_main(user_id)
    markup = InlineKeyboardMarkup()
    for name, checklist_id in checklists:
        checklist_name = '✔' if DB.is_activity_in_checklist(act_id, checklist_id) else '❌ '
        checklist_name += name
        callback_data = f'activity_to_checklists_{act_id}_{checklist_id}'
        markup.add(
            InlineKeyboardButton(checklist_name, callback_data=callback_data)
        )
    markup.add(InlineKeyboardButton('Подтвердить выбор', callback_data='accept_activities'))
    return markup


def gen_activity_measure_markup(activity_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Сделано - Не сделано', callback_data=f'measure_bool_{activity_name}'))
    markup.add(InlineKeyboardButton('Физическая величина', callback_data=f'measure_physics_{activity_name}'))
    return markup


#основной экран. разметка 2. редактировать чеклист
#переименовать/удалить чеклист/вернуться
def gen_checklist_settings_markup(checklist_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('Переименовать чеклист', callback_data=f'rename_checklist_{checklist_id}'))
    markup.add(InlineKeyboardButton('Удалить чеклист', callback_data=f'delete_checklist_{checklist_id}'))
    markup.add(InlineKeyboardButton('<- (вернуться)', callback_data=f'come_back_{checklist_id}'))
    return markup


#основной экран. разметка 3.
#вы уверены, что хотите удалить чеклист? активности останутся в других чеклистах
def gen_confirm_deleting_checklist_markup(checklist_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да", callback_data=f"delete_checklist_{checklist_id}"))
    markup.add(InlineKeyboardButton("Нет", callback_data=f"come_back_{checklist_id}"))
    return markup

dict_UTC = (
    ('-01:00', '(UTC-01:00) Cape Verde'),
    ('+00:00', '(UTC+00:00) Dublin, Edinburgh, Lisbon, London'),
    ('+01:00', '(UTC+01:00) Amsterdam, Berlin, Rome, Stockholm, Madrid, Paris, Belgrade, Budapest, Warsaw'),
    ('+02:00', '(UTC+02:00) Athens, Bucharest, Istanbul, Helsinki, Kyiv, Riga, Sofia, Cairo'),
    ('+03:00', '(UTC+03:00) Baghdad, Minsk, Kuwait, Riyadh, Nairobi'),
    ('+03:30', '(UTC+03:30) Tehran'),
    ('+04:00', '(UTC+04:00) Moscow, St. Petersburg, Volgograd, Tbilisi, Yerevan, Abu Dhabi, Baku'),
    ('+05:00', '(UTC+05:00) Tashkent'),
    ('+05:30', '(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi'),
    ('+05:45', '(UTC+05:45) Kathmandu'),
    ('+06:00', '(UTC+06:00) Astana, Yekaterinburg'),
)
