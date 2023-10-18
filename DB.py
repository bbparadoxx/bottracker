import os
import json
import datetime


base_user = '''{
  "info": {
    "status": "",
    "activity_name": ""
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


#трекает активность: 0 или 1
def track_activity(user_id, activity_name, status):
    current_date = str(datetime.date.today())
    path = f'users\\{user_id}.json'
    d = get_user_data(user_id)
    d['activities'][activity_name][current_date] = status
    json.dump(d, open(path, 'w'))


#добавляет активность
def add_activity(user_id, activity_name):
    d = get_user_data(user_id)
    d['activities'][activity_name] = {}
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w'))


#удаляет 1 активность
def delete_activity(user_id, activity_name):
    d = get_user_data(user_id)
    d['activities'].pop(activity_name)
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w'))


#удаляет все активности
def delete_all_activities(user_id):
    d = get_user_data(user_id)
    d['activities'].clear()
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w'))


#устанавливает статус активности
def set_current_activity(user_id, activity_name):
    d = get_user_data(user_id)
    d['info']['activity_name'] = activity_name
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w'))


#устанавливает статус действия
def set_current_status(user_id, status):
    d = get_user_data(user_id)
    d['info']['status'] = status
    path = f'users\\{user_id}.json'
    json.dump(d, open(path, 'w'))


#собирает статус действия
def get_user_status(user_id) -> str:
    return get_user_data(user_id)['info']['status']


#собирает статус активности
def get_user_current_activity(user_id) -> str:
    return get_user_data(user_id)['info']['activity_name']


#возвращает лист активностей пользователя
def get_activities_list(user_id):
    return get_user_data(user_id)['activities'].keys()


#проверяет, есть ли активность в списке активностей
def check_activity(user_id, activity_name) -> bool:
    return activity_name in get_user_data(user_id)['activities']


#счетчик активности для демонстрации
def count_track_relation(user_id, activity_name) -> str:
    d = get_user_data(user_id)
    return f'{sum(d["activities"][activity_name].values())}/{len(d["activities"][activity_name])}'


#Невошедшие приколы

#1. нужно для шедулера
# def get_user_ids() -> map:
#     path = 'users'
#     f = lambda name: int(name.split('.')[0])
#     return map(f, os.listdir(path))

#2 счетчик активности не дробью
# def count_track_abs(user_id) -> str:
#     return f'{sum(get_user_data(user_id).values())}'
