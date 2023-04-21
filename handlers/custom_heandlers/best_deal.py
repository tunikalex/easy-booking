from telebot import types
from loader import bot, api_key
from states.hotel_info import HotelInfoState
import requests
from telebot.types import Message
from . import calendars
from . import low_hightprice


@bot.message_handler(state=HotelInfoState.price_min)
def price_min(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        bot.send_message(message.from_user.id, f"{message.text} USD. I get it. \n"
                                               f"Enter MAXIMUM PRICE in USD per night")
        bot.set_state(message.from_user.id, HotelInfoState.price_max, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_min"] = int(message.text)
    else:
        bot.send_message(message.from_user.id, f"Price must be a number greater than zero. \n"
                                               f"Try entering the MINIMUM price again")

@bot.message_handler(state=HotelInfoState.price_max)
def price_max(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        # bot.send_message(message.from_user.id, f"{message.text} USD. I get it. \n"
        #                                        f"Now enter QUANTITY HOTELS, which do you want to see.")
        bot.send_message(message.from_user.id, f"{message.text} USD. I get it. \n"
                                               f"Let's find out the distance range at which "
                                               f"the hotel is located from the center. ")
        bot.set_state(message.from_user.id, HotelInfoState.measurements, message.chat.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        item_mile = types.InlineKeyboardButton(f"Miles", callback_data="mile")
        item_km = types.InlineKeyboardButton("Kilometers", callback_data="kilometer")
        markup.add(item_km, item_mile)
        bot.send_message(message.from_user.id, "What MEASURMENT SISTEM do you prefer?",
                         reply_markup=markup)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_max"] = int(message.text)
    else:
        bot.send_message(message.from_user.id, f"Price must be a number greater than zero. \n"
                                               f"Try entering the MAXIMUM price again")


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.measurements)
def measurments_call(call) -> None:
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data['measurement'] = call.data

    bot.send_message(call.from_user.id, "Enter the MINIMUM search RADIUS from the center: ")
    bot.set_state(call.from_user.id, HotelInfoState.distance_min)


@bot.message_handler(state=HotelInfoState.distance_min)
def distance_min(message: Message) -> None:
    distance: str = message.text.replace(',', '.')
    try:
        distance: float = float(distance)
        with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
            data['distance_min'] = distance
        bot.send_message(message.from_user.id, "Enter the MAXIMUM search RADIUS from the center: ")
        bot.set_state(message.from_user.id, HotelInfoState.distance_max)
    except ValueError:
        bot.send_message(message.from_user.id, "The distance can be either an integer or a fractional number. /n"
                                               "Try again. ")

@bot.message_handler(state=HotelInfoState.distance_max)
def distance_min(message: Message) -> None:
    distance: str = message.text.replace(',', '.')
    try:
        distance: float = float(distance)
        with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
            data['distance_max'] = distance
        bot.send_message(message.from_user.id, "Now enter QUANTITY HOTELS, which do you want to see.")
        bot.set_state(message.from_user.id, HotelInfoState.check_in)
    except ValueError:
        bot.send_message(message.from_user.id, "The distance can be either an integer or a fractional number. /n"
                                               "Try again. ")

