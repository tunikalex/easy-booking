import sqlite3
from telebot import types
from loader import bot, api_key
from states.hotel_info import HotelInfoState
import requests
from telebot.types import Message
from . import calendars
from .functions import high_low, hotels_detals, table_age, choose_need_pic, sql_input, sql_output
from datetime import datetime


@bot.message_handler(commands=['history'])
def history_servey(message: Message) -> None:
    markup_history = types.InlineKeyboardMarkup(row_width=2)
    item_history_3 = types.InlineKeyboardButton("3 last", callback_data="3 last")
    item_history_5 = types.InlineKeyboardButton("5 last", callback_data="5 last")
    item_history_today = types.InlineKeyboardButton("today", callback_data="today")
    item_history_all = types.InlineKeyboardButton("all", callback_data="all")
    markup_history.add(item_history_3, item_history_5, item_history_today, item_history_all)
    bot.send_message(message.from_user.id, "What period of history do you want to show?", reply_markup=markup_history)
    bot.set_state(message.from_user.id, HotelInfoState.history_output, message.chat.id)

@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.history_output)
def call_history(call):
    if call.data == "3 last":
        sql_output(message=call, extradition=3)
    elif call.data == "5 last":
        sql_output(message=call, extradition=5)
    elif call.data == "today":
        sql_output(message=call, today=True)
    else: # call.data == "all"
        sql_output(message=call)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def servey(message: Message) -> None:
    time_now = datetime.now()
    bot.set_state(message.from_user.id, HotelInfoState.search_location, message.chat.id)
    bot.send_message(message.from_user.id, f"Hello, {message.from_user.username}. \n"
                                           f"Enter city for hotels searching")

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data: dict
        data['command']: str = message.text[1::]
        data['command_time']: str = f'{time_now.day}-{time_now.month}-{time_now.year} {time_now.hour}:{time_now.minute}'


@bot.message_handler(state=HotelInfoState.search_location)
def search_location(message: Message):
    msg = bot.send_message(message.from_user.id, "Loading...")
    city_list = []
    url: str = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring: dict = {"q": message.text, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    headers: dict = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response: object = requests.request("GET", url, headers=headers, params=querystring).json()

    for i_object in response['sr']:
        if i_object["type"] in ("CITY", "NEIGHBORHOOD"):
            city_list.append(i_object)

    markup = types.InlineKeyboardMarkup(row_width=1)

    for i_city in city_list:  # выводим кнопки с названиями городов
        item_city = types.InlineKeyboardButton(i_city['regionNames']['fullName'],
                                               callback_data=i_city['gaiaId'])
        markup.add(item_city)  # добавляем название города с список кнопок

    bot.send_message(message.from_user.id, 'Choose interest location for you. '
                                           'Click the button.', reply_markup=markup)
    bot.delete_message(message.from_user.id, msg.message_id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cities_info'] = city_list  # Сохранили список найденыйх городов


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.search_location)
def call_city(call):  # реакция на нажатие кнопки с выбраной локацией
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        flag = False
        for i_city in data['cities_info']:
            if call.data == i_city['gaiaId']:
                data['location_id'] = str(data['cities_info'][0]['gaiaId'])  # Сохранили id локации
                data['location_name'] = data['cities_info'][0]['regionNames']['fullName']  # Полное название локации
                if data['command'] == 'lowprice' or data['command'] == 'highprice':
                    bot.send_message(call.from_user.id, "Now enter QUANTITY HOTELS, which do you want to see.")
                    bot.set_state(call.message.chat.id, HotelInfoState.check_in, call.message.chat.id)
                    flag = True
                else:
                    bot.set_state(call.message.chat.id, HotelInfoState.price_min, call.message.chat.id)
                    flag = True
                    bot.send_message(call.message.chat.id, "Thank you, I get it. \n"
                                                           "Now let's specify the range of prices you are interested \n"
                                                           "Enter MINIMUM PRICE in USD per night")
        if flag == False:
            bot.send_message(call.message.chat.id, f"Something don't work. \n"
                                                   f"Try agan")


@bot.message_handler(state=HotelInfoState.check_in)
def check_in(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
        if 'marker' in data:  # выполняется если дата введена неверно. Данные с ключом 'marker' уже созданы
            bot.send_message(message.from_user.id,
                             "So, please enter CHECK-IN date agen: ")
            data['marker'] = "check_in"
            bot.set_state(message.from_user.id, HotelInfoState.check_out)
            calendars.start_calendar(message=message)
        elif message.text.isdigit():  # выполняется если введено число при вводе количества отелей
            bot.send_message(message.from_user.id,
                             "All ok, please enter CHECK-IN date: ")
            data['quantity_hotels'] = int(message.text)  # количество отелей для вывода
            data['marker'] = "check_in"
            calendars.start_calendar(message=message)  # запускаем календарь для выбора даты заселения
            bot.set_state(message.from_user.id, HotelInfoState.check_out, message.chat.id)
        else:  # выполняется если при вводе количества отелей ввели не число
            bot.send_message(message.from_user.id, f"Dear {message.from_user.username}, "
                                                   f"quantity must have only numbers.")


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.check_out)
def check_out(call, flag=None) -> None:
    if call.data == 'yes' or flag == 1:  # Если дата заселения введена правильно
        bot.send_message(call.from_user.id, "Thank you, I get it. Select your CHECK-OUT date now")
        bot.set_state(call.from_user.id, HotelInfoState.room)
        with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
            data['marker'] = "check_out"
            calendars.start_calendar(message=call)
    else:  # если пользователь ошибся при вводе даты заселения
        bot.set_state(call.from_user.id, HotelInfoState.check_in)
        check_in(message=call)


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.room)
def room(call):
    if call.data == 'yes':  # Если дата выселения введена правильно
        bot.send_message(call.from_user.id, "All right, now we need to understand how many visitors are planned. \n"
                                            "Enter HOW MANY ADULTS there will be: ")
        bot.set_state(call.from_user.id, HotelInfoState.adults)
    else:
        bot.set_state(call.from_user.id, HotelInfoState.check_out)
        check_out(call=call, flag=1)


@bot.message_handler(state=HotelInfoState.adults)
def quantity_adults(message: Message) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item_0 = types.InlineKeyboardButton("No kids", callback_data='no')
        item_1 = types.InlineKeyboardButton("Have children", callback_data='yes')
        markup.add(item_0, item_1)
        bot.send_message(message.from_user.id, 'Super. '
                                               '\nBy clicking on the button, indicate whether there will be children: '
                         , reply_markup=markup)
        bot.set_state(message.chat.id, HotelInfoState.kids, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['adults'] = int(message.text)

    else:
        bot.send_message(message.from_user.id, "Quantity must have number "
                                               "\nand cannot be zero. "
                                               "\nTry agan. ")


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.kids)
def call_kids(call):  # реакция на нажатие кнопки c наличием или отсутствием детей
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data["have_children"] = call.data
        data['children']: list = []

    if call.data == 'no':
        bot.send_message(call.message.chat.id, f"Without kids. I get it.")
        choose_need_pic(message=call)
    else:
        bot.set_state(call.message.chat.id, HotelInfoState.amount_children, call.message.chat.id)
        bot.send_message(call.message.chat.id, f"You have children. Super! "
                                               f"\nHow much?")


check_in


@bot.message_handler(state=HotelInfoState.amount_children)
def amount_children(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, f"Good! So let's write. ")
        table_age(message=message)
        bot.set_state(message.from_user.id, HotelInfoState.kids_age, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_children'] = int(message.text)
    else:
        bot.send_message(message.from_user.id, "Quantity must have number "
                                               "\nand cannot be zero. "
                                               "\nTry agan. ")


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.kids_age)
def call_age_children(call) -> None:
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        kids_list: list = data['children']
        kids_list.append({"age": int(call.data)})

        if len(kids_list) == data['amount_children']:
            bot.send_message(call.message.chat.id, f"Super! ")
            choose_need_pic(message=call)
        else:
            table_age(message=call)


@bot.callback_query_handler(func=lambda call: True, state=HotelInfoState.quantity_pic)
def quanyity_pic(call) -> None:
    quantity_pic = int(call.data)
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data['quantity_pic'] = quantity_pic

    if data['command'] == 'lowprice' or data['command'] == 'highprice' or data['command'] == 'bestdeal':
        high_low(message=call)
        bot.set_state(call.from_user.id, HotelInfoState.result)
    else:
        bot.send_message(call.from_user.id, "Something don't work. ")


@bot.callback_query_handler(func=lambda call: True,
                            state=HotelInfoState.result)
def call_result(call):
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data: dict
        all_hotels = data['all_hotels']
        hotel_id = call.data
        for i_hotel in all_hotels:
            if i_hotel['id'] == hotel_id:
                data['hotel_info']: dict = i_hotel
                data['distanceFromCenter']: float = float(
                    i_hotel['destinationInfo']['distanceFromDestination']['value'])
                data['cost_per_night']: int = int(i_hotel['price']['lead']['formatted'][1::])
                data['total_cost'] = data['rent_days'] * data['cost_per_night']
                data['hotel_id']: str = hotel_id

                found_hotels = ''
                for i_num, i_hotel in enumerate(data['found_hotels']):
                    found_hotels += str(i_num + 1) + ": " + i_hotel + "\n"

                user_id: str = str(call.from_user.id)

                db_data = (data['command_time'], data['command'], data['location_name'], found_hotels,
                           data['hotel_info']['name'], data['cost_per_night'], data['rent_days'])

                sql_output(user_id=user_id, db_data=db_data)

    hotels_detals(message=call)
    data.pop('all_hotels')
    #
    # print('\nDATA keys: ')
    # for i in data.items():  # контроль сохранённых данных, вывод на консоль
    #     print(i)
