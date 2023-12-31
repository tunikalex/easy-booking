from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loader import bot
import datetime
from telebot import types


def date_confirmation(call, result):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item_y = types.InlineKeyboardButton("Yes", callback_data='yes')
    item_n = types.InlineKeyboardButton("No", callback_data='no')
    markup.add(item_y, item_n)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=types.InlineKeyboardMarkup([]))
    bot.send_message(call.from_user.id, f"You selected {result} Is the date entered correct?", reply_markup=markup)

def start_calendar(message) -> None:
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.from_user.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(call):
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}", call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
            if result < datetime.date.today():  # если введена дата из прошлого
                bot.send_message(call.from_user.id, "You cannot select a date from the past. Try again ")
                start_calendar(message=call)
            elif data['marker'] == 'check_in':
                data["date_check_in"] = result  # дата заселения
                date_confirmation(call=call, result=result)
            elif data['marker'] == 'check_out':
                data["date_check_out"] = result  # дата выселения
                date_confirmation(call=call, result=result)
            else:
                bot.send_message(call.from_user.id, "Something wrong. We are already work it. ")
