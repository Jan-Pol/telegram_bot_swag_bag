import datetime

from telebot import types
import calendar


def create_calendar(year, month):
    now = datetime.date.today()
    markup = types.InlineKeyboardMarkup()
    # First row - Month and Year
    row = [types.InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data="ignore")]
    markup.row(*row)
    # Second row - Week Days
    week_days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    row = []
    for day in week_days:
        row.append(types.InlineKeyboardButton(day, callback_data="ignore"))
    markup.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                then = datetime.date(year, month, day)
                delta = now - then
                if delta.days > 0:
                    row.append(types.InlineKeyboardButton(str(day), callback_data="calendar_day " + str(day) + " " + str(month) + " " + str(year)))
                else:
                    row.append(types.InlineKeyboardButton(str(day), callback_data="calendar_day " + str(day) + " " + str(month) + " " + str(year)))
        markup.row(*row)
    row = [types.InlineKeyboardButton("Сегодня", callback_data="calendar_day " + str(datetime.date.today().day) + " " + str(month) + " " + str(year))]
    markup.row(*row)
    row = [types.InlineKeyboardButton("Назад", callback_data='main_menu')]
    markup.row(*row)
    return markup
