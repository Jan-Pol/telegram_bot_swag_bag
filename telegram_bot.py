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


@bot.message_handler(commands=['start'])
@error_handler
def start(message):
    """Запрос ввода номера телефона и сверка его с БД, в случае успеха: вывод шлавного меню"""
    chat_id = message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Старт'])
    message_to_send = telegram_pages.start()
    bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)


@bot.message_handler(content_types=['text'])
@error_handler
def text_handler(message):
    chat_id = message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Старт'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Главное меню'])
        message_to_send = telegram_pages.verify_number_phone(chat_id, message.text)
        bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)
    elif CALLBACK_DATA['Выбрать тип задачи'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введен релиз'])
        message_to_send = telegram_pages.input_empty_release(chat_id, message.text)
        bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)
    elif CALLBACK_DATA['Введен релиз'] == current_user_state:
        if any(map(str.isdigit, message.text)):
            user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены трудозатраты'])
            message_to_send = telegram_pages.input_time(chat_id, message.text)
            bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)
        else:
            text_handler()
    elif CALLBACK_DATA['Введены трудозатраты'] == current_user_state:
        if any(map(str.isdigit, message.text)):
            user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены артефакты'])
            message_to_send = telegram_pages.input_empty_artifacts(chat_id, message.text)
            bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)
        else:
            text_handler()
    elif CALLBACK_DATA['Введены артефакты'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введено описание'])
        message_to_send = telegram_pages.input_description(chat_id, message.text)
        bot.send_message(chat_id=chat_id, text=message_to_send.message_text, reply_markup=message_to_send.markup)
    else:
        return


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Главное меню'])
@error_handler
def get_main_menu_from_outside(call):
    """Создание главного меню по событию из произвольного экрана"""
    chat_id = call.message.chat.id
    message_to_send = telegram_pages.create_main_menu(call=call)
    bot.edit_message_text(chat_id=chat_id, text=message_to_send.message_text, message_id=call.message.message_id,
                          reply_markup=message_to_send.markup)


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать день календаря'] in call.data)
@error_handler
def select_kind_of_activity(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    match = re.search(str(constans.REG_DATE), call.data)
    date = datetime.datetime.strptime(match[0], '%d %m %Y').strftime('%d.%m.%Y')
    if CALLBACK_DATA['Внести трудозатраты'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Выбрать день календаря"])
        message_to_send = telegram_pages.select_kind_of_activity(chat_id, date)

        bot.edit_message_text("Выбран день: " + str(date) + "\nВыберите вид деятельности:", call.from_user.id, call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Внести трудозатраты'])
@error_handler
def select_work_day(call):
    """Предложение внести трудозатраты"""
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Внести трудозатраты"])
    message_to_send = telegram_pages.select_work_day()
    bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=message_to_send.markup)
    bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Статистика за неделю'])
@error_handler
def stats_for_week(call):
    """Статистика за неделю"""
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Статистика за неделю'])
    message_to_send = telegram_pages.stats_for_week()
    bot.edit_message_text("Статистика за неделю хорошая", call.from_user.id, call.message.message_id, reply_markup=message_to_send.markup)
    bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == CALLBACK_DATA['Текущий проект'])
@error_handler
def current_project(call):
    """Текущий проект"""
    chat_id = call.message.chat.id
    user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Текущий проект"])
    message_to_send = telegram_pages.current_project()
    bot.edit_message_text("Текущий проект = ВСЕРОД", call.from_user.id, call.message.message_id, reply_markup=message_to_send.markup)
    bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать вид деятельности'] in call.data)
@error_handler
def select_as(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    match = re.search(str(constans.NUMERAL), call.data)
    koa_id = match[0]
    koa_name = call.data[3:].replace(koa_id, "")
    if CALLBACK_DATA['Выбрать день календаря'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA["Выбрать вид деятельности"])
        message_to_send = telegram_pages.select_as(chat_id, koa_name)
        bot.edit_message_text("Выбран вид деятельности:  " + koa_name + "\nВыберите АС:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать АС'] in call.data)
@error_handler
def select_type_task(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    match = re.search(str(constans.NUMERAL), call.data)
    as_id = match[0]
    as_name = call.data[2:].replace(as_id, "")
    if CALLBACK_DATA['Выбрать вид деятельности'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Выбрать АС'])
        message_to_send = telegram_pages.select_type_task(chat_id, as_name)
        bot.edit_message_text("Выбрана АС:  " + as_name + "\nВыберите тип задачи:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Выбрать тип задачи'] in call.data)
@error_handler
def input_release(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    match = re.search(str(constans.NUMERAL), call.data)
    tt_id = match[0]
    tt_name = call.data[2:].replace(tt_id, "")
    if CALLBACK_DATA['Выбрать АС'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Выбрать тип задачи'])
        message_to_send = telegram_pages.input_release(chat_id, tt_name)
        bot.edit_message_text("Выбран тип задачи:  " + tt_name + "\nВведите название релиза:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введен релиз'] in call.data)
@error_handler
def input_empty_release(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Выбрать тип задачи'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введен релиз'])
        message_to_send = telegram_pages.input_empty_release(chat_id, '')
        bot.edit_message_text("Название релиза не указано:\nВведите количество отработанного времени:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введены трудозатраты'] in call.data)
@error_handler
def input_time(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Введен релиз'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены трудозатраты'])
        message_to_send = telegram_pages.input_time(chat_id, 8)
        bot.edit_message_text("Количество отработанного времени 8 часов:\nВведите количество артефактов:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Введены артефакты'] in call.data)
@error_handler
def input_artifacts(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Введены трудозатраты'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Введены артефакты'])
        message_to_send = telegram_pages.input_empty_artifacts(chat_id, 0)
        bot.edit_message_text("Количество артефактов не указано\nВведите описание:", call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


@bot.callback_query_handler(func=lambda call: CALLBACK_DATA['Конец'] in call.data)
@error_handler
def finish(call):
    chat_id = call.message.chat.id
    current_user_state = user_state.get_user_state(user_id=chat_id)
    if CALLBACK_DATA['Введено описание'] == current_user_state:
        user_state.set_user_state(user_id=chat_id, state=CALLBACK_DATA['Конец'])
        message_to_send = telegram_pages.finish_write_work_time(chat_id)
        bot.edit_message_text(message_to_send.message_text, call.from_user.id,
                              call.message.message_id, reply_markup=message_to_send.markup)
        bot.answer_callback_query(call.id, text="")
    else:
        return


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(config.POLLING_INTERVAL)
