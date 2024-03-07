import psycopg2
import datetime
from settings import db_settings
from datetime import datetime, timedelta
from pytz import timezone


def is_user_in_db(telegram_id: int) -> bool:
    cursor = db_connection.cursor()
    select = f"SELECT * FROM users WHERE telegram_id = {telegram_id}"
    cursor.execute(select)
    records = cursor.fetchall()
    cursor.close()
    return bool(records)


def get_user_id(telegram_id: int) -> int:
    cursor = db_connection.cursor()
    select = f"SELECT id FROM users WHERE telegram_id = {telegram_id}"
    cursor.execute(select)
    records = cursor.fetchall()
    cursor.close()
    return int(records[0][0])


#создаёт файл пользователя
def create_user(user_data: dict) -> int:
    insert = (
        "INSERT INTO users (telegram_id, UTC) "
        "VALUES (%s, %s) "
        "RETURNING id "
    )
    cursor = db_connection.cursor()
    cursor.execute(insert, tuple(user_data.values()))
    user_id = cursor.fetchone()[0]
    db_connection.commit()
    cursor.close()
    return user_id


#создаёт основной чеклист пользователя
def create_main_checklist(user_id):
    create_checklist(user_id, 'Main checklist')


#проверяет, есть ли чеклист
def is_checklist_in_db(user_id, checklist_name) -> bool:
    cursor = db_connection.cursor()
    select = f"SELECT * FROM checklists WHERE owner = {user_id} and name = '{checklist_name}'"
    cursor.execute(select)
    records = cursor.fetchall()
    cursor.close()
    return bool(records)


#создает чеклист!
def create_checklist(user_id, checklist_name) -> int:
    cursor = db_connection.cursor()
    insert = (
            "INSERT INTO checklists (owner, name, is_main) "
            "VALUES (%s, %s, %s) "
            "RETURNING id "
        )
    cursor.execute(insert, (user_id, checklist_name, bool(checklist_name == "Main checklist")))
    activity_id = cursor.fetchone()[0]
    db_connection.commit()
    cursor.close()
    return activity_id


# До сих пор работает (поставили с Серёжей
# добавляет активность!
def create_activity(user_id, activity_name, is_bool, measurement):
    cursor = db_connection.cursor()
    insert = (
        "INSERT INTO activities (name, creation_date, owner, is_bool, measurement) "
        "VALUES (%s, %s, %s, %s, %s) "
        "RETURNING id "
    )
    cursor.execute(insert, (activity_name, get_date(user_id), user_id, is_bool, measurement))
    activity_id = cursor.fetchone()[0]
    db_connection.commit()
    cursor.close()
    # нужна функция, которая ищет id чеклиста у пользователя, как минимум мэин чеклиста
    # вызываем функцию добавления в чеклист для мэин чеклиста
    set_activity_to_checklist(activity_id, get_main_checklist_id(user_id))


#ищет id мэйн чеклиста пользователя !
def get_main_checklist_id(user_id):
    select = (
        "SELECT id FROM checklists  "
        f"WHERE  owner = {user_id} and is_main = true"
    )
    cursor = db_connection.cursor()
    cursor.execute(select)
    checklist_id = cursor.fetchone()[0]
    db_connection.commit()
    cursor.close()
    return checklist_id


#определяет актуальную дату пользователя!
def get_date(user_id):
    cursor = db_connection.cursor()
    select = f"SELECT UTC FROM users WHERE id = {user_id} "
    cursor.execute(select)
    user_utc = cursor.fetchone()[0]
    cursor.close()
    fmt = "%Y-%m-%d %H:%M:%S"
    user_data = datetime.now(timezone('UTC')) + timedelta(hours=user_utc)
    return user_data.strftime(fmt)


#добавляет активность в несколько чеклистов!
def set_activity_to_checklists(activity: int, checklists: list):
    for checklist in checklists:
        set_activity_to_checklist(activity, checklist)


#добавляет несколько активностей в 1 чеклист!
def set_checklist_to_activities(checklist: int, activities: list):
    for activity in activities:
        set_activity_to_checklist(activity, checklist)


#добавляет активность в чеклист!
def set_activity_to_checklist(act_id: int, checklist_id: int):
    cursor = db_connection.cursor()
    insert = (
        "INSERT INTO activities_checklists (act_id, checklist_id) "
        "VALUES (%s, %s) "
    )
    cursor.execute(insert, (act_id, checklist_id))
    db_connection.commit()
    cursor.close()


#проверяет, есть ли активность!
def is_activity_in_db(user_id, activity_name) -> bool:
    cursor = db_connection.cursor()
    select = f"SELECT * FROM activities WHERE owner = {user_id} and name = '{activity_name}'"
    cursor.execute(select)
    records = cursor.fetchall()
    cursor.close()
    return bool(records)


def is_activity_in_checklist(activity_id, checklist_id) -> bool:
    cursor = db_connection.cursor()
    select = (
        f"SELECT * FROM activities_checklists "
        f"WHERE checklist_id = {checklist_id} and act_id = '{activity_id}'"
    )
    cursor.execute(select)
    records = cursor.fetchall()
    cursor.close()
    return bool(records)


#проверка типа активности на 1/0!
def is_activity_bool(activity_id):
    cursor = db_connection.cursor()
    select = f"SELECT is_bool FROM activities WHERE id = {activity_id} "
    cursor.execute(select)
    activity = cursor.fetchone()[0]
    cursor.close()
    return bool(activity)


#обновляет трэк!
def update_track(activity_id, track, date):
    cursor = db_connection.cursor()
    update = (
        "UPDATE tracks "
        f"SET act_id = {activity_id}, _value = {int(track)}, _date = '{date}' "
    )
    cursor.execute(update)
    db_connection.commit()
    cursor.close()


#обновляет трэк на противоположной,только для активностей 1/0!
def update_reverse_track(activity_id, date):
    cursor = db_connection.cursor()
    update = (
        "UPDATE tracks "
        f"SET act_id = {activity_id}, _value = {int(not get_track(activity_id, date))}, _date = '{date}'"
    )
    cursor.execute(update)
    db_connection.commit()
    cursor.close()


#отдаёт список активностей пользователя!
def get_activities(user_id) -> list:
    cursor = db_connection.cursor()
    select = f"SELECT * FROM activities WHERE owner = {user_id} "
    cursor.execute(select)
    lt = cursor.fetchall()
    # print(lt)
    # names = [item for t in lt for item in t]
    cursor.close()
    # return names
    return lt

#отдаёт id активности по имени!
def get_activity_id(user_id, activity_name) -> int:
    cursor = db_connection.cursor()
    select = f"SELECT id FROM activities WHERE owner = {user_id} and name = '{activity_name}'"
    cursor.execute(select)
    activity_id = cursor.fetchone()[0]
    cursor.close()
    return activity_id


#отдаёт id чеклиста по имени!
def get_checklist_id(user_id, checklist_name) -> int:
    cursor = db_connection.cursor()
    select = f"SELECT id FROM checklists WHERE owner = {user_id} and name = '{checklist_name}'"
    cursor.execute(select)
    checklist_id = cursor.fetchone()[0]
    cursor.close()
    return checklist_id


#создает трэк!
def create_track(act_id, value, date):
    cursor = db_connection.cursor()
    insert = (
            "INSERT INTO tracks (act_id, _date, _value) "
            "VALUES (%s, %s, %s) "
        )
    cursor.execute(insert, (act_id, date, int(value)))
    db_connection.commit()
    cursor.close()


#отдает трэк!
def get_track(activity_id, date):
    cursor = db_connection.cursor()
    select = f"SELECT _value FROM tracks WHERE act_id = {activity_id} and _date = '{date}'"
    cursor.execute(select)
    track_value = cursor.fetchone()[0]
    cursor.close()
    return track_value


#отдает активности в чеклисте!
def get_activities_from_checklist(checklist_id):
    cursor = db_connection.cursor()
    select = (
        "SELECT name FROM activities_checklists as a_c "
        "LEFT JOIN activities as a "
        "on a_c.act_id = a.id " 
        f"WHERE checklist_id = {checklist_id}"
    )
    cursor.execute(select)
    lt = cursor.fetchall()
    names = [item for t in lt for item in t]
    cursor.close()
    return names


#отдает чеклисты пользователя!
def get_checklists(user_id):
    cursor = db_connection.cursor()
    select = (
        "SELECT name FROM checklists "
        f"WHERE owner = {user_id}"
    )
    cursor.execute(select)
    lt = cursor.fetchall()
    names = [item for t in lt for item in t]
    cursor.close()
    return names


#отдаёт все чеклисты с активностью!
def get_checklists_with_activity(activity_id):
    cursor = db_connection.cursor()
    select = (
        "SELECT checklist_id FROM activities_checklists "
        f"WHERE act_id  = {activity_id} "
    )
    cursor.execute(select)
    lt = cursor.fetchall()
    checklist_ids = [item for t in lt for item in t]
    cursor.close()
    return checklist_ids


#удалить чеклист!
def delete_checklist(checklist_id):
    cursor = db_connection.cursor()
    delete = (
        "DELETE FROM checklists "
        f"WHERE id = {checklist_id}"
    )
    cursor.execute(delete)
    db_connection.commit()
    cursor.close()


#удалить активность!
def delete_activity(activity_id):
    cursor = db_connection.cursor()
    delete = (
        "DELETE FROM activities "
        f"WHERE id = {activity_id}"
    )
    cursor.execute(delete)
    db_connection.commit()
    cursor.close()


#удалить активность из чеклиста!
def delete_activity_from_checklist(activity_id, checklist_id):
    cursor = db_connection.cursor()
    delete = (
        "DELETE FROM activities_checklists "
        f"WHERE act_id = {activity_id} and checklist_id = {checklist_id}"
    )
    cursor.execute(delete)
    db_connection.commit()
    cursor.close()


#удалить активность из всех чеклистов!
def delete_activity_from_checklists(activity_id,  checklists: list):
    for checklist_id in checklists:
        delete_activity_from_checklist(activity_id, checklist_id)


#удалить все активности из чеклиста!
def delete_activities_from_checklist(activities: list,  checklist):
    for activity_id in activities:
        delete_activity_from_checklist(activity_id, checklist)


#переименовать чеклист!
def update_checklist_name(checklist_id, new_checklist_name):
    cursor = db_connection.cursor()
    update = (
        "UPDATE checklists "
        f"SET name = '{new_checklist_name}' "
        f"WHERE id = {checklist_id}"
    )
    cursor.execute(update)
    db_connection.commit()
    cursor.close()


#переименовать активность!!
def update_activity_name(activity_id, new_activity_name):
    cursor = db_connection.cursor()
    update = (
        "UPDATE activities "
        f"SET name = '{new_activity_name}' "
        f"WHERE id = {activity_id}"
    )
    cursor.execute(update)
    db_connection.commit()
    cursor.close()


#установить более раннюю дату создания активности!!
def update_creation_date(activity_id, date):
    cursor = db_connection.cursor()
    update = (
        "UPDATE activities "
        f"SET creation_date = '{date}' "
        f"WHERE id = {activity_id}"
    )
    cursor.execute(update)
    db_connection.commit()
    cursor.close()


db_connection = psycopg2.connect(**db_settings)

# test_id = 21
# print(is_user_in_db(test_id)) # ТЕСТИРУЕМ РАБОТОСПОСОБНОСТЬ
# user = create_user({'telegram_id': test_id, 'UTC': -2})
# print(user)
# print(is_user_in_db(test_id))
# print(is_checklist_in_db(user, 'Main checklist'))
# create_main_checklist(user)
# print(is_checklist_in_db(user, 'Main checklist'))


# create_activity(19, 'Веселиться с черепашками',True, '-')
# print(is_activity_in_db(19, 'Веселиться с черепашками'))
# print(is_activity_in_db(19, 'Веселица с черепашками'))
# print(is_activity_in_db(7, 'Веселиться с черепашками'))

# create_activity(19, 'Есть пирожные', True, '-')
# create_activity(19, 'Прогуляться пешком до работы', True, '-')

# print(is_activity_in_db(19, 'Есть пирожные'))
# print(is_activity_in_db(19, 'Прогуляться пешком до работы'))
#
# # create_checklist(19, 'Любимые занятия')
# # create_checklist(19, 'Обычный вторник')
# # create_checklist(19, 'Экоклуб')
#
# print(is_checklist_in_db(19, 'Любимые занятия'))
# print(is_checklist_in_db(19, 'Обычный вторник'))
# print(is_checklist_in_db(19, 'Экоклуб'))


# set_activity_to_checklist(get_activity_id(19, 'Есть пирожные'), get_checklist_id(19, 'Любимые занятия'))
# set_checklist_to_activities(get_checklist_id(19, 'Обычный вторник'),
#                             [get_activity_id(19, 'Прогуляться пешком до работы'),
#                             get_activity_id(19, 'Веселиться с черепашками')]
#                             )
# set_activity_to_checklists(get_activity_id(19, 'Веселиться с черепашками'),
#                            [get_checklist_id(19, 'Экоклуб'), get_checklist_id(19, 'Любимые занятия')]
#                           )

# act_id_test_1 = get_activity_id(19, 'Есть только вкусные пирожные')
# print(get_activities(19))
# print('111111111111')
# act_id_test_2 = get_activity_id(19, 'Веселиться с черепашками')
# print('222222222')
# checklist_id_test_1 = get_checklist_id(19, "Любимые занятия")
# print('33333333')
# # checklist_id_test_2 = get_checklist_id(19, "Обычный четверг")
# # print('44444444444')
#
# fmt = '%Y-%m-%d'
# # create_track(act_id_test_1, True, datetime.today().strftime(fmt))
# update_track(act_id_test_1, False, datetime.today().strftime(fmt))
# print('5555555')
#
# print(is_activity_bool(act_id_test_1))
# update_reverse_track(act_id_test_1, datetime.today().strftime(fmt))
# print('6666666')
#
# print(get_activities(19))
# print('7777')
# print(get_checklist_id(19, "Любимые занятия"))
# print('8888')
# print(get_track(act_id_test_1, datetime.today().strftime(fmt)))
# print('9999')
# print(get_activities_from_checklist(checklist_id_test_1))
# print('1010')
# print(get_checklists(19))
# print('1212')
# print(get_checklists_with_activity(act_id_test_1))
# print('1313')
#
# # create_activity(19, 'Тестирую код',True, '-')
# print('1414')
#
# # update_checklist_name(checklist_id_test_2, "Обычный понедельник")
# # print('1515')
# #
# checklist_id_test_2 = get_checklist_id(19, "Обычный понедельник")
# print('1616')
#
# # update_activity_name(act_id_test_1, 'Есть только вкусные пирожные')
# # print('1717')
# update_creation_date(act_id_test_1, datetime(2020, 5, 17).strftime(fmt))
# print('1818')
#
# delete_checklist(checklist_id_test_2)
# print('1919')
# delete_activity(act_id_test_2)
# print('2020')
# delete_activity_from_checklist(act_id_test_1, checklist_id_test_1)
# print('2121')
# print(get_checklists_with_activity(act_id_test_1))
# delete_activity_from_checklists(act_id_test_1, get_checklists_with_activity(act_id_test_1))
# print('2323')
# delete_activities_from_checklist(get_activities_from_checklist(checklist_id_test_1),  checklist_id_test_1)
# print('2424')




