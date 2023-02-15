import datetime
from telebot import types
from loader import bot
from states.hotel_info import HotelInfoState
import requests
from telebot.types import Message


def lowprice(message, location_id, quantity_hotels):
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": location_id},
        "checkInDate": {
            "day": datetime.datetime.now().day,
            "month": datetime.datetime.now().month,
            "year": datetime.datetime.now().year
        },
        "checkOutDate": {
            "day": datetime.datetime.now().day,
            "month": datetime.datetime.now().month,
            "year": datetime.datetime.now().year
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 1}, {"age": 6}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": quantity_hotels,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 1500,
            "min": 1
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "7d19e92effmsh5e7fc0b7bddd944p1675d6jsn97fc9214874f",  # Изменить на RAPID_API_KEY в .env
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("POST", url, json=payload, headers=headers).json()

    bot.send_message(message.from_user.id,
                     "Below you will find a list of hotels. From cheap to expensive")
    marcup = types.InlineKeyboardMarkup(row_width=1)
    for i_hotel in response['data']['propertySearch']['properties']:
        item = types.InlineKeyboardButton(i_hotel['name'], callback_data=i_hotel['id'])
        marcup.add(item)
    bot.send_message(message.from_user.id, 'Choose interest HOTEL for you.\n'
                                           ' And click the button.', reply_markup=marcup)


def hightprice(message, location_id, quantity_hotels):
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": location_id},
        "checkInDate": {
            "day": datetime.datetime.now().day,
            "month": datetime.datetime.now().month,
            "year": datetime.datetime.now().year
        },
        "checkOutDate": {
            "day": datetime.datetime.now().day,
            "month": datetime.datetime.now().month,
            "year": datetime.datetime.now().year
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 1}, {"age": 6}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": quantity_hotels,
        "sort": "PRICE_HIGHT_TO_LOW",
        "filters": {"price": {
            "max": 15000,
            "min": 1
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "7d19e92effmsh5e7fc0b7bddd944p1675d6jsn97fc9214874f",  # Изменить на RAPID_API_KEY в .env
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("POST", url, json=payload, headers=headers).json()

    bot.send_message(message.from_user.id,
                     "Below you will find a list of hotels. From cheap to expensive")
    marcup = types.InlineKeyboardMarkup(row_width=1)
    for i_hotel in response['data']['propertySearch']['properties']:
        item = types.InlineKeyboardButton(i_hotel['name'], callback_data=i_hotel['id'])
        marcup.add(item)
    bot.send_message(message.from_user.id, 'Choose interest HOTEL for you.\n'
                                           ' And click the button.', reply_markup=marcup)


@bot.message_handler(commands=['lowprice', 'hightprice'])
def servey(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelInfoState.search_location, message.chat.id)
    bot.send_message(message.from_user.id, f"Hello, {message.from_user.username}. \n"
                                           f"Enter city for hotels searching")

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = message.text[1::]


@bot.message_handler(state=HotelInfoState.search_location)
def search_location(message: Message):
    city_list = list()
    url: str = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring: dict = {"q": message.text, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    headers: dict = {
        "X-RapidAPI-Key": "7d19e92effmsh5e7fc0b7bddd944p1675d6jsn97fc9214874f",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response: object = requests.request("GET", url, headers=headers, params=querystring).json()

    for i_object in response['sr']:
        if i_object['type'] == 'CITY':
            city_list.append(i_object)

    markup = types.InlineKeyboardMarkup(row_width=1)

    if len(city_list) == 1:
        item_0 = types.InlineKeyboardButton(city_list[0]['regionNames']['fullName'],
                                            callback_data='city_0')
        markup.add(item_0)
    elif len(city_list) == 2:
        item_0 = types.InlineKeyboardButton(city_list[0]['regionNames']['fullName'],
                                            callback_data='city_0')
        item_1 = types.InlineKeyboardButton(city_list[1]['regionNames']['fullName'],
                                            callback_data='city_1')
        markup.add(item_0, item_1)
    elif len(city_list) == 3:
        item_0 = types.InlineKeyboardButton(city_list[0]['regionNames']['fullName'],
                                            callback_data='city_0')
        item_1 = types.InlineKeyboardButton(city_list[1]['regionNames']['fullName'],
                                            callback_data='city_1')
        item_2 = types.InlineKeyboardButton(city_list[2]['regionNames']['fullName'],
                                            callback_data='city_2')
        markup.add(item_0, item_1, item_2)
    else:
        item_no = types.InlineKeyboardButton("Unfortunately I can't search this city name. ",
                                            callback_data='no_city')
        markup.add(item_no)

    bot.send_message(message.from_user.id, 'Choose interest location for you. '
                                           'Click the button.', reply_markup=markup)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cities_info'] = city_list


@bot.callback_query_handler(func=lambda call: True,
                            state=HotelInfoState.search_location)
def call_city(call):
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        if call.data == 'city_0':
            data['location_id'] = data['cities_info'][0]['gaiaId']
            data['location_name'] = data['cities_info'][0]['regionNames']['fullName']
            bot.send_message(call.message.chat.id, "Thank you, I get it. \n"
                                                   "Now enter quantity hotels, which do you want to see.")
            bot.set_state(call.message.chat.id, HotelInfoState.quantity_hotels, call.message.chat.id)
        elif call.data == 'city_1':
            data['location_id'] = data['cities_info'][1]['gaiaId']
            data['location_name'] = data['cities_info'][1]['regionNames']['fullName']
            bot.send_message(call.message.chat.id, "Thank you, I get it. \n"
                                                   "Now enter quantity hotels, which do you want to see.")
            bot.set_state(call.message.from_user.id, HotelInfoState.quantity_hotels, call.message.chat.id)
        elif call.data == 'city_3':
            data['location_id'] = data['cities_info'][2]['gaiaId']
            data['location_name'] = data['cities_info'][2]['regionNames']['fullName']
            bot.send_message(call.message.chat.id, "Thank you, I get it. \n"
                                                   "Now enter quantity hotels, which do you want to see.")
            bot.set_state(call.message.from_user.id, HotelInfoState.quantity_hotels, call.message.chat.id)
        elif call.data == 'no_city':
            bot.send_message(call.message.chat.id, "Try agen! \nEnter city for hotels searching.")
            bot.set_state(call.message.from_user.id, HotelInfoState.search_location, call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, f"Socallmething don't work. ")
            bot.set_state(call.message.chat.id, HotelInfoState.quantity_hotels, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: True,
                            state=[i for i in [HotelInfoState.quantity_pic, HotelInfoState.need_pic]])
def call_hotel_id(call):
    bot.send_message(call.message.chat.id, f"Your HOTEL id: {call.data}")   #Добавить целевое действие
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data['hotel_id'] = call.data
    bot.delete_state(call.from_user.id)


@bot.message_handler(state=HotelInfoState.quantity_hotels)
def get_quantityhotels(messege: Message) -> None:
    if messege.text.isdigit():
        bot.send_message(messege.from_user.id, "Thank you, I get it. "
                                               "Should I show you some pictures from those hotels? (Y/N)")
        bot.set_state(messege.from_user.id, HotelInfoState.need_pic, messege.chat.id)

        with bot.retrieve_data(messege.from_user.id, messege.chat.id) as data:
            data['quantity_hotels'] = messege.text
    else:
        bot.send_message(messege.from_user.id, f"Dear {messege.from_user.username}, quantity must have only numbers.")


@bot.message_handler(state=HotelInfoState.need_pic)
def get_needpic(message: Message) -> None:
    if message.text.lower() in ('y', 'yes', 'д', 'да'):
        bot.send_message(message.from_user.id, "Thank you. I see you need to look at some pictures. Good! \n "
                                               "How many photos should I show for you? Please enter a number.")
        bot.set_state(message.from_user.id, HotelInfoState.quantity_pic, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_pic'] = message.text
    elif message.text.lower() in ('n', 'no', 'н', 'нет'):
        bot.send_message(message.from_user.id,
                         "Thank you. I see you don't need to look at some pictures. \n"
                         "As you wish!")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_pic'] = message.text
            if data['command']  == 'lowprice':
                lowprice(message=message, location_id=data['location_id'], quantity_hotels=int(data['quantity_hotels']))
            elif data['command']  == 'hightprice':
                hightprice(message=message, location_id=data['location_id'], quantity_hotels=int(data['quantity_hotels']))
            else:
                bot.send_message(message.from_user.id, "Something don't work. ", message.chat.id)
    else:
        bot.send_message(message.from_user.id, f"Dear {message.from_user.username}, I don't understand you.\n"
                                               f"Please, choose 'Y' or 'N'.")


@bot.message_handler(state=HotelInfoState.quantity_pic)
def get_quanyity_pic(message: Message) -> None:
    inform_flag = True
    if message.text.isdigit() and int(message.text) <= 10:
        bot.send_message(message.from_user.id, f"Thank you. I promise remember this. \n"
                                               f"I will show you {message.text} photos")
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['quantity_pic'] = message.text
    elif message.text.isdigit() and int(message.text) > 10:
        bot.send_message(message.from_user.id, f"unfortunately I can't show more than 10 photos. \n"
                                               f"So I'll show you what I can")
    else:
        bot.send_message(message.from_user.id, f"Dear {message.from_user.username}, I don't understand you.\n"
                                                  f"Please, enter a number.")
        inform_flag = False

    if inform_flag == True and data['command'] == 'lowprice':
        lowprice(message=message, location_id=data['location_id'], quantity_hotels=int(data['quantity_hotels']))
    elif inform_flag == True and data['command'] == 'hightprice':
        hightprice(message=message, location_id=data['location_id'], quantity_hotels=int(data['quantity_hotels']))
    else:
        bot.send_message(message.from_user.id, "Something don't work. ", message.chat.id)
