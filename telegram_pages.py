from telebot import types
from callback_data import CALLBACK_DATA
import datetime
import telegramcalendar
import user_state
from db_helper import db_helper
from google_sheets_helper import gsh_helper
import user_data


class Message:

    def __init__(self, message_text, markup):
        self.message_text = message_text
        self.markup = markup


def start():
    message_text = 'Введите номер телефона:'
    new_message = Message(message_text=message_text, markup='')
    return new_message


def create_main_menu(message=None, call=None):
    """Создание главного меню.
    Один из параметров message/call должен быть not None

    Args:
        message: сообщение от пользователя
        call: вызов от кнопки

    Returns:
        new_message - готовое сообщение с главным меню
    """
    if message is None and call is None:
        raise Exception('Один из параметров message/call должен быть not None')
    if call is not None:
        message = call.message
    try:
        chat_id = message.chat.id

    except AttributeError:
        chat_id = message

    if not db_helper.check_user_existence(chat_id):
        db_helper.create_user(message=message)

    user_name = db_helper.get_user_name_with_chat_id(chat_id)
    user_data.record_to_dict(chat_id, 'fio', user_name)
    markup = types.InlineKeyboardMarkup()
    message_text = user_name + '\nГлавное меню:'

    text = 'Внести трудозатраты'
    markup.row(types.InlineKeyboardButton(text, callback_data=CALLBACK_DATA['Внести трудозатраты']))

    text = 'Статистика за неделю'
    markup.row(types.InlineKeyboardButton(text, callback_data=CALLBACK_DATA['Статистика за неделю']))

    text = 'Текущий проект'
    markup.row(types.InlineKeyboardButton(text, callback_data=CALLBACK_DATA['Текущий проект']))

    new_message = Message(message_text=message_text, markup=markup)

    return new_message


def select_work_day():
    now = datetime.datetime.now()
    message_text = 'Выберите дату:'
    markup = telegramcalendar.create_calendar(now.year, now.month)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def select_kind_of_activity(chat_id, date):
    markup = types.InlineKeyboardMarkup()
    message_text = "Выбран день: " + str(date) + "\nВыберите вид деятельности:"
    koa_list = db_helper.get_kind_of_activity()
    for i in range(len(koa_list)):
        markup.row(types.InlineKeyboardButton(koa_list[i], callback_data='koa' + str(koa_list[i]) + str(i)))
    user_data.record_to_dict(chat_id, 'date', date)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def select_as(chat_id, koa_name):
    markup = types.InlineKeyboardMarkup()
    message_text = "Выбран вид деятельности:  " + koa_name + "\nВыберите АС:"
    as_list = db_helper.get_as()
    for i in range(len(as_list)):
        markup.row(types.InlineKeyboardButton(as_list[i], callback_data='as' + str(as_list[i]) + str(i)))
    user_data.record_to_dict(chat_id, 'koa_name', koa_name)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def select_type_task(chat_id, as_name):
    markup = types.InlineKeyboardMarkup()
    message_text = '"Выбрана АС:  " + as_name + "\nВыберите тип задачи:"'
    type_task_list = db_helper.get_type_task()
    for i in range(len(type_task_list)):
        markup.row(types.InlineKeyboardButton(type_task_list[i], callback_data='tt' + str(type_task_list[i]) + str(i)))
    user_data.record_to_dict(chat_id, 'as_name', as_name)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def input_release(chat_id, tt_name):
    markup = types.InlineKeyboardMarkup()
    message_text = "Выбран тип задачи:  " + tt_name + "\nВведите название релиза:"
    markup.row(types.InlineKeyboardButton('Пропустить', callback_data='input_rel'))
    user_data.record_to_dict(chat_id, 'tt_name', tt_name)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def verify_number_phone(chat_id, number_phone):
    certified_users_dict = db_helper.get_certified_users_dict(chat_id, number_phone)
    if certified_users_dict == 0:
        message_text = 'Указанный номер отсутствует в БД'
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Старт'])
        new_message = Message(message_text=message_text, markup='')
    else:
        user_data.record_to_dict(chat_id, 'fio', certified_users_dict.get('fio'))
        new_message = create_main_menu(message=certified_users_dict.get('id'))
    return new_message


def input_empty_release(chat_id, release_desc):
    markup = types.InlineKeyboardMarkup()
    message_text = "Название релиза не указано:\nВведите количество отработанного времени:"
    markup.row(types.InlineKeyboardButton('8 часов', callback_data='input_time'))
    user_data.record_to_dict(chat_id, 'release', release_desc)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def input_time(chat_id, time):
    markup = types.InlineKeyboardMarkup()
    message_text = 'Количество отработанного времени 8 часов:\nВведите количество артефактов:'
    markup.row(types.InlineKeyboardButton('Пропустить', callback_data='input_art'))
    try:
        time = int(time)
    except ValueError:
        time = str(time)
        maketrans = time.maketrans
        time = time.translate(maketrans('.', ','))
    user_data.record_to_dict(chat_id, 'time', time)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def input_empty_artifacts(chat_id, artifacts):
    message_text = "Количество артефактов не указано\nВведите описание:"
    markup = ''
    user_data.record_to_dict(chat_id, 'artifacts', artifacts)
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def input_description(chat_id, description):
    markup = types.InlineKeyboardMarkup()
    user_data.record_to_dict(chat_id, 'description', description)
    message_text = 'Текущая запись: \
                    \nВид деятельности: ' + str(user_data.record_dict.get(chat_id).get('koa_name')) + \
                   '\nАС: ' + str(user_data.record_dict.get(chat_id).get('as_name')) + \
                   '\nТип задачи: ' + str(user_data.record_dict.get(chat_id).get('tt_name')) + \
                   '\nРелиз: ' + str(user_data.record_dict.get(chat_id).get('release')) + \
                   '\nТрудозатраты: ' + str(user_data.record_dict.get(chat_id).get('time')) + ' часов' + \
                   '\nКоличество артефактов: ' + str(user_data.record_dict.get(chat_id).get('artifacts')) + \
                   '\nОписание: ' + str(user_data.record_dict.get(chat_id).get('description'))
    markup.row(types.InlineKeyboardButton('Сохранить запись', callback_data='finish'))
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def finish_write_work_time(chat_id):
    record_list = [i for i in user_data.record_dict.get(chat_id).values()]
    gsh_helper.update_google_sheet(record_list)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Главное меню', callback_data=CALLBACK_DATA['Главное меню']))
    new_message = Message(message_text='Запись сохранена.', markup=markup)
    return new_message


def stats_for_week():
    markup = types.InlineKeyboardMarkup()
    message_text = "Статистика за неделю хорошая"
    text = 'Назад'
    markup.row(types.InlineKeyboardButton(text, callback_data=CALLBACK_DATA['Главное меню']))
    new_message = Message(message_text=message_text, markup=markup)
    return new_message


def current_project():
    markup = types.InlineKeyboardMarkup()
    message_text = "Текущий проект = ВСЕРОД"
    text = 'Назад'
    markup.row(types.InlineKeyboardButton(text, callback_data=CALLBACK_DATA['Главное меню']))
    new_message = Message(message_text=message_text, markup=markup)
    return new_message
