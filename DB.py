import os
import json
import datetime


base_user = '''{
  "info": {
    "state": "",
    "activity_name": ""
  },
  "activities" : {
  }
}'''


def get_user_data(user_id) -> dict:
    path = f'users\\{user_id}.json'
    d = json.loads(open(path, 'r', encoding='utf-8').read())
    return d


def create_user(user_id: int) -> None:
    path = f'users\\{user_id}.json'
    if not(os.path.exists(path) and os.path.isfile(path)):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(base_user)


def get_user_ids() -> map:
    path = 'users'
    f = lambda name: int(name.split('.')[0])
    return map(f, os.listdir(path))


def track_activity(user_id, activity_name, status):
    current_date = str(datetime.date.today())
    path = f'users\\{user_id}.json'
    get_user_data(user_id)['activities'][activity_name][current_date] = status
    json.dump(get_user_data(user_id), open(path, 'w'))


def add_activity(user_id, activity_name):
    get_user_data(user_id)['activities'][activity_name] = {}
    path = f'users\\{user_id}.json'
    json.dump(get_user_data(user_id), open(path, 'w'))


def set_current_activity(user_id, activity_name):
    get_user_data(user_id)['info']['activity_name'] = activity_name
    path = f'users\\{user_id}.json'
    json.dump(get_user_data(user_id), open(path, 'w'))


def set_current_status(user_id, status):
    get_user_data(user_id)['info']['status'] = status
    path = f'users\\{user_id}.json'
    json.dump(get_user_data(user_id), open(path, 'w'))


def get_user_status(user_id) -> str:
    return get_user_data(user_id)['info']['state']


def get_user_current_activity(user_id) -> str:
    return get_user_data(user_id)['info']['activity']


def check_activity(user_id, activity_name) -> bool:
    return activity_name in get_user_data(user_id)['activities']


def get_activities_list(user_id):
    return get_user_data(user_id)['activities'].keys()


def count_track_relation(user_id) -> str:
    return f'{sum(get_user_data(user_id).values())}/{len(get_user_data(user_id))}'


def count_track_abs(user_id) -> str:
    return f'{sum(get_user_data(user_id).values())}'