import logging
import time
import traceback
import telebot
import user_state
from telebot import apihelper
from telebot.types import CallbackQuery, Message
import config
import telegram_pages
from callback_data import CALLBACK_DATA
import constans
import re
import datetime


TOKEN = config.token
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
apihelper.proxy = {'https': f'https://lexy898:100293@35.228.164.201:3128'}
bot = telebot.TeleBot(TOKEN)


def error_handler(func):
    def decorator(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as err:
            message_text = 'Что-то пошло не так. Попробуйте, пожалуйста, снова.'
            if isinstance(args[0], CallbackQuery):
                bot.answer_callback_query(callback_query_id=args[0].id, text=message_text)
                message_to_send = telegram_pages.create_main_menu(call=args[0])
                bot.edit_message_text(chat_id=args[0].message.chat.id, text=message_to_send.message_text,
                                      message_id=args[0].message.message_id, reply_markup=message_to_send.markup)
            elif isinstance(args[0], Message):
                bot.send_message(chat_id=args[0].chat.id, text=message_text)
                message_to_send = telegram_pages.create_main_menu(message=args[0])
                bot.send_message(chat_id=args[0].chat.id, text=message_to_send.message_text,
                                 reply_markup=message_to_send.markup)
            tb_str = traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)
            logger.error(f'Error in Telegram Bot handler. Traceback: {tb_str}')
    return decorator


def message_handler(operation):
    def decorator(func):
        def wrapper(*args, **kwargs):
            message_received, message_to_send = func(*args, **kwargs)
            if operation == 'edit':
                try:
                    bot.edit_message_text(chat_id=message_received.message.chat.id,
                                          text=message_to_send.message_text,
                                          message_id=message_received.message.message_id,
                                          reply_markup=message_to_send.markup)
                except Exception as err:
                    pass
            if operation == 'send':
                try:
                    bot.send_message(chat_id=message_received.chat.id,
                                     text=message_to_send.message_text,
                                     reply_markup=message_to_send.markup)
                except Exception as err:
                    pass
            return message_received, message_to_send
        return wrapper
    return decorator


@bot.message_handler(commands=['start'])
@error_handler
@message_handler('send')
def start(message):
    """Запрос ввода номера телефона и сверка его с БД, в случае успеха: вывод главного меню"""
    user_state.set_user_state(user_id=message.chat.id, state=CALLBACK_DATA['Старт'])
    message_to_send = telegram_pages.start()
    return message, message_to_send


@bot.message_handler(content_types=['text'])
@error_handler
@message_handler('send')
def text_handler(message):
    chat_id = message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Старт'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Главное меню'])
        message_to_send = telegram_pages.verify_number_phone(chat_id, message.text)
        return message, message_to_send
    elif CALLBACK_DATA['Выбрать тип задачи'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введен релиз'])
        message_to_send = telegram_pages.input_empty_release(chat_id, message.text)
        return message, message_to_send
    elif CALLBACK_DATA['Введен релиз'] == current_user_state:
        if any(map(str.isdigit, message.text)):
            user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены трудозатраты'])
            message_to_send = telegram_pages.input_time(chat_id, message.text)
            return message, message_to_send
        else:
            text_handler()
    elif CALLBACK_DATA['Введены трудозатраты'] == current_user_state:
        if any(map(str.isdigit, message.text)):
            user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены артефакты'])
            message_to_send = telegram_pages.input_empty_artifacts(chat_id, message.text)
            return message, message_to_send
        else:
            text_handler()
    elif CALLBACK_DATA['Введены артефакты'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введено описание'])
        message_to_send = telegram_pages.input_description(chat_id, message.text)
        return message, message_to_send


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Главное меню'])
@error_handler
@message_handler('edit')
def get_main_menu_from_outside(call):
    """Создание главного меню по событию из произвольного экрана"""
    message_to_send = telegram_pages.create_main_menu(call=call)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать день календаря'] in call.data)
@error_handler
@message_handler('edit')
def select_kind_of_activity(call):
    chat_id = call.message.chat.id
    match = re.search(str(constans.REG_DATE), call.data)
    date = datetime.datetime.strptime(match[0], '%d %m %Y').strftime('%d.%m.%Y')
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Выбрать день календаря"])
    message_to_send = telegram_pages.select_kind_of_activity(chat_id, date)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Внести трудозатраты'])
@error_handler
@message_handler('edit')
def select_work_day(call):
    user_state.set_user_state(user_id=call.message.chat.id, state=CALLBACK_DATA["Внести трудозатраты"])
    message_to_send = telegram_pages.select_work_day()
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Статистика за неделю'])
@error_handler
@message_handler('edit')
def stats_for_week(call):
    """Статистика за неделю"""
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Статистика за неделю'])
    message_to_send = telegram_pages.stats_for_week()
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Текущий проект'])
@error_handler
@message_handler('edit')
def current_project(call):
    """Текущий проект"""
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Текущий проект"])
    message_to_send = telegram_pages.current_project()
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать вид деятельности'] in call.data)
@error_handler
@message_handler('edit')
def select_as(call):
    chat_id = call.message.chat.id
    match = re.search(str(constans.NUMERAL), call.data)
    koa_id = match[0]
    koa_name = call.data[3:].replace(koa_id, "")
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Выбрать вид деятельности"])
    message_to_send = telegram_pages.select_as(chat_id, koa_name)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать АС'] in call.data)
@error_handler
@message_handler('edit')
def select_type_task(call):
    chat_id = call.message.chat.id
    match = re.search(str(constans.NUMERAL), call.data)
    as_id = match[0]
    as_name = call.data[2:].replace(as_id, "")
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Выбрать АС'])
    message_to_send = telegram_pages.select_type_task(chat_id, as_name)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать тип задачи'] in call.data)
@error_handler
@message_handler('edit')
def input_release(call):
    chat_id = call.message.chat.id
    match = re.search(str(constans.NUMERAL), call.data)
    tt_id = match[0]
    tt_name = call.data[2:].replace(tt_id, "")
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Выбрать тип задачи'])
    message_to_send = telegram_pages.input_release(chat_id, tt_name)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введен релиз'] in call.data)
@error_handler
@message_handler('edit')
def input_empty_release(call):
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введен релиз'])
    message_to_send = telegram_pages.input_empty_release(chat_id, '')
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введены трудозатраты'] in call.data)
@error_handler
@message_handler('edit')
def input_time(call):
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены трудозатраты'])
    message_to_send = telegram_pages.input_time(chat_id, 8)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введены артефакты'] in call.data)
@error_handler
@message_handler('edit')
def input_artifacts(call):
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены артефакты'])
    message_to_send = telegram_pages.input_empty_artifacts(chat_id, 0)
    return call, message_to_send


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Конец'] in call.data)
@error_handler
@message_handler('edit')
def finish(call):
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Конец'])
    message_to_send = telegram_pages.finish_write_work_time(chat_id)
    return call, message_to_send


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(config.POLLING_INTERVAL)
