import DB

#основной экран. разметка 1. выбрать другой чеклист для трэка + создать чеклист
#разметка чеклистов(+чеклист всех активностей) + add checklist
def gen_markup_show_another_checklist(user_id):
    checklists = DB.get_checklists(user_id)
    markup = InlineKeyboardMarkup()
    markup.row_width = len(checklist) + 1
    for checklist_name in checklists:
        markup.add(InlineKeyboardButton(checklist, callback_data=f"cb_choose_{checklist}"))
    markup.add(InlineKeyboardButton('Создать чеклист', callback_data='add checklist'))
    return markup


#основной экран. разметка 2. редактировать чеклист
#переименовать/удалить чеклист/вернуться
def gen_markup(checklist_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('Переименовать чеклист', callback_data='Rename checklist'))
    markup.add(InlineKeyboardButton('Удалить чеклист', callback_data='delete checklist'))
    markup.add(InlineKeyboardButton('<- (вернуться)', callback_data='come back'))
    return markup

вы уверены, что хотите удалить чеклист? активности останутся в других чеклистах
#основной экран. разметка 3.
#переименовать/удалить чеклист/вернуться
def gen_markup(checklist_id):

    return markup

переименовать/ удалить активность/вернуться?
#основной экран. разметка 2. редактировать чеклист
#переименовать/удалить чеклист/вернуться
def gen_markup(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(InlineKeyboardButton('Переименовать чеклист', callback_data='Rename checklist'))
    markup.add(InlineKeyboardButton('Удалить чеклист', callback_data='delete checklist'))
    markup.add(InlineKeyboardButton('<- (вернуться)', callback_data='come back'))
    return markup

удалить активность из чеклиста или совсем?

вы уверены, что хотите удалить активность и все ваши записи о ней?

разметка активностей (выбери все) + создать новую