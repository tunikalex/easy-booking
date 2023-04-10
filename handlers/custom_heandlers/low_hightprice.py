from telebot import types
from loader import bot, api_key
from states.hotel_info import HotelInfoState
import requests
from telebot.types import Message
from . import calendars


def high_low(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
        location_id = data['location_id']
        quantity_hotels = data['quantity_hotels']
        adults = data['adults']
        children = data['children']
        date_check_in = data["date_check_in"]
        date_check_out = data["date_check_out"]
        if data['command'] == 'lowprice' or data['command'] == 'highprice':
            pricemin = 1
            pricemax = 3600
        else:
            pricemin = data['price_min']
            pricemax = data['price_max']
        if pricemin > pricemax:  # минимальная цена должна быть меньше максимальной
            pricemin, pricemax = pricemax, pricemin
        if date_check_in > date_check_out:  # Дата заселения должна быть меньше даты выселения
            date_check_in, date_check_out = date_check_out, date_check_in
        data['rent_days']: int = int((date_check_out - date_check_in).days)

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": str(location_id)},
        "checkInDate": {
            "day": date_check_in.day,
            "month": date_check_in.month,
            "year": date_check_in.year
        },
        "checkOutDate": {
            "day": date_check_out.day,
            "month": date_check_out.month,
            "year": date_check_out.year
        },
        "rooms": [
            {
                "adults": adults,
                "children": children
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": pricemax,
            "min": pricemin
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers).json()
    try:
        hotels = response["data"]["propertySearch"]["properties"]
    except:
        bot.send_message(message.from_user.id, "I can not find hotels in the city you are interested in. \n"
                                               "Please retry your request.")
        bot.delete_state(message.from_user.id)


    markup_hotel = types.InlineKeyboardMarkup(row_width=1)
    with bot.retrieve_data(message.from_user.id) as data:
        data['all_hotels'] = hotels
        if data['command'] == 'highprice':
            hotels = reversed(hotels)

        for ikey, i_hotel in enumerate(hotels):
            item_hotel = types.InlineKeyboardButton(
                f"{i_hotel['name']} | {i_hotel['price']['lead']['formatted']} per night",
                callback_data=i_hotel['id'])
            markup_hotel.add(item_hotel)
            if ikey == int(quantity_hotels) - 1:
                break
        bot.send_message(message.from_user.id, 'CHOOSE interest hotel for you', reply_markup=markup_hotel)


def hotels_detals(message: Message):
    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:

        propertyId = data['hotel_id']
        quanyity_pic = data['quantity_pic']
        distanceFromCenter = data['distanceFromCenter']
        cost_per_night = data['cost_per_night']
        total_cost = data['total_cost']


    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": propertyId
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    response = requests.request("POST", url, json=payload, headers=headers).json()

    medias: list = []
    hotel_name = response["data"]["propertyInfo"]["summary"]["name"]
    address = response['data']['propertyInfo']['summary']['location']['address']['addressLine']
    photos = response['data']['propertyInfo']['propertyGallery']['images']

    if quanyity_pic > 0:  # срабатывет, если количество фотографий больше нуля
        for i_ind, i_image in enumerate(photos):
            if int(i_ind) == int(quanyity_pic):
                break
            image_url: str = i_image["image"]["url"]
            medias.append(types.InputMediaPhoto(image_url))

        bot.send_media_group(chat_id=message.from_user.id, media=medias)
        bot.send_message(message.from_user.id, f"{quanyity_pic} pictures of hotel {hotel_name}: ")

    bot.send_message(message.from_user.id, f"Short information about this hotel: \n"
                                           f"Hotel's name: {hotel_name} \n"
                                           f"Address: {address} \n"
                                           f"Distance from center: {distanceFromCenter} miles\n"
                                           f"Cost per night: {cost_per_night} USD\n"
                                           f"Total cost for all rent: {total_cost} USD")

    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
        data["photos"] = medias
        data['hotel_name'] = hotel_name
        data['address'] = address

    bot.set_state(message.from_user.id, HotelInfoState.result)


def table_age(message: Message) -> None:
    markup = types.InlineKeyboardMarkup(row_width=3)
    for j_age in range(0, 18, 3):
        item_kid_age_1 = types.InlineKeyboardButton(f"{j_age}", callback_data=str(j_age))
        item_kid_age_2 = types.InlineKeyboardButton(f"{j_age+1}", callback_data=str(j_age+1))
        item_kid_age_3 = types.InlineKeyboardButton(f"{j_age+2}", callback_data=str(j_age+2))
        markup.add(item_kid_age_1, item_kid_age_2, item_kid_age_3)
    bot.send_message(message.from_user.id, "Now tell me how old they are: ",
                     reply_markup=markup)

def choose_need_pic(message: Message) -> None:
    markup = types.InlineKeyboardMarkup(row_width=5)
    for i in range(1, 11):
        item_i = types.InlineKeyboardButton(f"{i}", callback_data=f'{i}')
        markup.add(item_i)
    item_0 = types.InlineKeyboardButton("Without photos", callback_data='0')
    markup.add(item_0)
    bot.send_message(message.from_user.id, "How many PHOTOS of the hotel would you like to see? ", reply_markup=markup)
    bot.set_state(message.from_user.id, HotelInfoState.quantity_pic)


@bot.message_handler(commands=['lowprice', 'highprice'])
def servey(message: Message) -> None:
    bot.set_state(message.from_user.id, HotelInfoState.search_location, message.chat.id)
    bot.send_message(message.from_user.id, f"Hello, {message.from_user.username}. \n"
                                           f"Enter city for hotels searching")

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data: dict
        data['command'] = message.text[1::]


@bot.message_handler(state=HotelInfoState.search_location)
def search_location(message: Message):
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
        markup.add(item_city) # добавляем название города с список кнопок

    bot.send_message(message.from_user.id, 'Choose interest location for you. '
                                           'Click the button.', reply_markup=markup)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cities_info'] = city_list  # Сохранили список найденыйх городов


@bot.callback_query_handler(func=lambda call: True,
                            state=HotelInfoState.search_location)
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


@bot.message_handler(state=HotelInfoState.price_min)
def price_min(message: Message):
    if message.text.isdigit() and int(message.text) > 0:
        bot.send_message(message.from_user.id, f"{message.text} USD. I get it. \n"
                                               f"Enter MAXIMUM PRICE in USD per night")
        bot.set_state(message.from_user.id, HotelInfoState.price_max, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_min"] = int(message.text)
    else:
        bot.send_message(message.chat.id, f"Price must be a number greater than zero. \n"
                                          f"Try entering the MINIMUM price again",
                         message.chat.id)


@bot.message_handler(state=HotelInfoState.price_max)
def price_max(message: Message):
    if message.text.isdigit() and int(message.text) > 0:
        bot.send_message(message.from_user.id, f"{message.text} USD. I get it. \n"
                                               f"Now enter QUANTITY HOTELS, which do you want to see.")
        bot.set_state(message.from_user.id, HotelInfoState.check_in, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["price_max"] = int(message.text)
    else:
        bot.send_message(message.chat.id, f"Price must be a number greater than zero. \n"
                                          f"Try entering the MAXIMUM price again",
                         message.chat.id)


@bot.message_handler(state=HotelInfoState.check_in)
def check_in(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if 'marker' in data:  # выполняется если дата введена неверно. Данные с ключом 'marker' уже созданы
            bot.send_message(message.from_user.id,
                             "So, please enter CHECK-IN date agen: ")
            data['marker'] = "check_in"
            bot.set_state(message.from_user.id, HotelInfoState.check_out, message.chat.id)
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


@bot.message_handler(state=HotelInfoState.check_out)
def check_out(message: Message, flag = None) -> None:
    if message.text.lower() in ("y", "yes", "д", "да") or flag == 1:  # Если дата заселения введена правильно
        bot.send_message(message.from_user.id, "Thank you, I get it. Select your CHECK-OUT date now")
        bot.set_state(message.from_user.id, HotelInfoState.room, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['marker'] = "check_out"
            calendars.start_calendar(message=message)
    else:  # если пользователь ошибся при вводе даты заселения
        bot.set_state(message.from_user.id, HotelInfoState.check_in, message.chat.id)
        check_in(message=message)


@bot.message_handler(state=HotelInfoState.room)
def room(message):
    if message.text.lower() in ("y", "yes", "д", "да"):  # Если дата выселения введена правильно
        bot.send_message(message.from_user.id, "All right, now we need to understand how many visitors are planned. \n"
                                               "Enter HOW MANY ADULTS there will be: ")
        bot.set_state(message.from_user.id, HotelInfoState.adults, message.chat.id)
    else:
        bot.set_state(message.from_user.id, HotelInfoState.check_out, message.chat.id)
        check_out(message=message, flag=1)


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
                                               "\nTry agan. ",
                         message.chat.id)


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

    if data['command'] == 'lowprice' or data['command'] == 'highprice':
        high_low(message=call)
        bot.set_state(call.from_user.id, HotelInfoState.result)
    else:
        bot.send_message(call.from_user.id, "Something don't work. ", call.chat.id)


@bot.callback_query_handler(func=lambda call: True,
                            state=HotelInfoState.result)
def call_result(call):
    bot.send_message(call.message.chat.id, f"Your HOTEL id: {call.data}")

    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data: dict
        all_hotels = data['all_hotels']
        hotel_id = call.data
        for i_hotel in all_hotels:
            if i_hotel['id'] == hotel_id:
                data['hotel_info']: dict = i_hotel
                data['distanceFromCenter']: float = float(i_hotel['destinationInfo']['distanceFromDestination']['value'])
                data['cost_per_night']: int = int(i_hotel['price']['lead']['formatted'][1::])
                data['total_cost'] = data['rent_days'] * data['cost_per_night']
                data['hotel_id']: str = hotel_id

    hotels_detals(message=call)
    data.pop('all_hotels')
    bot.delete_state(call.from_user.id)

    # print('\nDATA keys: ')
    # for i in data.items():  # контроль сохранённых данных, вывод на консоль
    #     print(i)
