import os
import json
import datetime
from datetime import timedelta

base_user = '''{
  "info": {
    "status": "",
    "activity_name": "",
    "date_for_change" : ""
  },
  "activities_creation": {
  },
  "activities" : {
  }
}'''


#открывает доступ к файлу пользователя в виде словаря
def get_user_data(user_id) -> dict:
    path = f'users\\{user_id}.json'
    d = json.loads(open(path, 'r', encoding='utf-8').read())
    return d


#создаёт файл пользователя
def create_user(user_id: int) -> None:
    path = f'users\\{user_id}.json'
    if not(os.path.exists(path) and os.path.isfile(path)):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(base_user)


# добавляет активность
def add_activity(user_id, activity_name):
    d = get_user_data(user_id)
    current_date = str(datetime.date.today())
    d['activities'][activity_name] = {}
    d['activities_creation'][activity_name] = current_date
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w',encoding='utf-8'))


#трекает активность: 0 или 1
def track_activity(user_id, activity_name, status):
    current_date = str(datetime.date.today())
    d = get_user_data(user_id)
    d['activities'][activity_name][current_date] = status
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


#удаляет 1 активность
def delete_activity(user_id, activity_name):
    d = get_user_data(user_id)
    d['activities'].pop(activity_name)
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


#удаляет все активности
def delete_all_activities(user_id):
    d = get_user_data(user_id)
    d['activities'].clear()
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


# устанавливает статус действия
def set_current_status(user_id, status):
    d = get_user_data(user_id)
    d['info']['status'] = status
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


#устанавливает статус активности
def set_current_activity(user_id, activity_name):
    d = get_user_data(user_id)
    d['info']['activity_name'] = activity_name
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


#устанавливает дату для изменения
def set_current_date_for_change(user_id, date):
    d = get_user_data(user_id)
    d['info']['date_for_change'] = date
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w', encoding='utf-8'))


#собирает статус действия
def get_user_status(user_id) -> str:
    return get_user_data(user_id)['info']['status']


#собирает статус активности
def get_user_current_activity(user_id) -> str:
    return get_user_data(user_id)['info']['activity_name']


#собирает дату для изменения
def get_user_date_for_change(user_id) -> str:
    return get_user_data(user_id)['info']['date_for_change']


#возвращает лист активностей пользователя
def get_activities_list(user_id):
    return get_user_data(user_id)['activities'].keys()


#проверяет, есть ли активность в списке активностей
def check_activity(user_id, activity_name) -> bool:
    return activity_name in get_user_data(user_id)['activities']


#счетчик активности для демонстрации
def count_track_relation(user_id, activity_name) -> str:
    d = get_user_data(user_id)
    creation_date = datetime.datetime.strptime(d["activities_creation"][activity_name], '%Y-%m-%d')
    current_date = datetime.datetime.today()
    delta = (current_date - creation_date).days + 1
    return f'{sum(d["activities"][activity_name].values())}/{delta}'


#показывает трек по запросу дня
def show_track(user_id, activity_name, date) -> str:
    d = get_user_data(user_id)
    if date in d["activities"][activity_name].keys():
        return f'{d["activities"][activity_name][date]}'
    else:
        return 'Нет ометки'


#меняет трек по запросу дня
def change_track(new_score, user_id, activity_name, date):
    path = f'users\\{user_id}.json'
    d = get_user_data(user_id)
    d["activities"][activity_name][date] = new_score
    creation_date = datetime.datetime.strptime(d["activities_creation"][activity_name], '%Y-%m-%d')
    change_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    if change_date < creation_date:
        d["activities_creation"][activity_name] = date
    json.dump(d, open(path, 'w', encoding='utf-8'))


#переименовать активность
def rename_activity(user_id, new_name, old_name):
    path = f'users\\{user_id}.json'
    d = get_user_data(user_id)
    d["activities"][new_name] = d["activities"].pop(old_name)
    d["activities_creation"][new_name] = d["activities_creation"].pop(old_name)
    json.dump(d, open(path, 'w', encoding='utf-8'))


def collect_all_data_toshow(user_id, start_date, end_date):
    d = get_user_data(user_id)
    current_date = datetime.datetime.today()
    matrix = []
    matrix_i = []
    day_list = []
    act_list = []
    for n in range(int((end_date - start_date).days) + 1):
        _date = (start_date + timedelta(n)).strftime('%Y-%m-%d')
        y, m, day = _date.split('-')
        day_list.append((int(day), int(m)))
    for act in get_activities_list(user_id):
        creation_date = datetime.datetime.strptime(d["activities_creation"][act], '%Y-%m-%d')
        if creation_date <= end_date:
            act_list.append(act)
            for n in range(int((end_date - start_date).days) + 1):
                date = start_date + timedelta(n)
                date_str = date.strftime('%Y-%m-%d')
                if date > current_date:
                    matrix_i.append(None)
                elif date < creation_date:
                    matrix_i.append(-1)
                elif date_str in d["activities"][act].keys():
                    matrix_i.append(d["activities"][act][date_str])
                else:
                    matrix_i.append(0)
            matrix.append(matrix_i)
            matrix_i = []
    return act_list, day_list, matrix


def collect_acts_toshow(user_id, start_date):
    d = get_user_data(user_id)
    act_list = []
    for act in get_activities_list(user_id):
        creation_date = datetime.datetime.strptime(d["activities_creation"][act], '%Y-%m-%d')
        if creation_date <= start_date:
            act_list.append(act)
    return act_list

def collect_dates_toshow(start, end):
    day_list = []
    for n in range(int((end - start).days) + 1):
        _date = (start + timedelta(n)).strftime('%Y-%m-%d')
        y, m, day = _date.split('-')
        day_list.append((int(day), int(m)))
    return day_list

#Невошедшие приколы

#1. нужно для шедулера
# def get_user_ids() -> map:
#     path = 'users'
#     f = lambda name: int(name.split('.')[0])
#     return map(f, os.listdir(path))

#2 счетчик активности не дробью
# def count_track_abs(user_id) -> str:
#     return f'{sum(get_user_data(user_id).values())}'
