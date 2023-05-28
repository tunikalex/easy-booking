from telebot import types
from loader import bot, api_key
from states.hotel_info import HotelInfoState
import requests
from telebot.types import Message
import sqlite3
from . import calendars


def high_low(message: Message) -> None:
    msg = bot.send_message(message.from_user.id, "Loading...")

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
        bot.send_message(message.from_user.id, "I can not find hotels in the city you are interested in.")
        bot.delete_state(message.from_user.id)

    try:
        markup_hotel = types.InlineKeyboardMarkup(row_width=1)
        with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
            data['all_hotels'] = hotels
            if data['command'] == 'highprice':
                hotels = reversed(hotels)markup_hotel
            elif data['command'] == 'bestdeal':
                if data['measurement'] == 'kilometer':
                    data['distance_min'] *= 0.6214
                    data['distance_max'] *= 0.6214
                hotels_distance = []
                for i_hotel in hotels:
                    distance_condition = data['distance_min'] \
                                         <= i_hotel['destinationInfo']['distanceFromDestination']['value'] <= \
                                         data['distance_max']
                    if distance_condition:
                        hotels_distance.append(i_hotel)
                hotels = hotels_distance
            else:
                pass

            found_hotels: list = []
            for ikey, i_hotel in enumerate(hotels):
                found_hotels.append(i_hotel['name'])
                item_hotel = types.InlineKeyboardButton(
                    f"{i_hotel['name']} | {i_hotel['price']['lead']['formatted']} per night",
                    callback_data=i_hotel['id'])
                markup_hotel.add(item_hotel)
                if ikey == int(quantity_hotels) - 1:
                    break
            data['found_hotels'] = found_hotels
            bot.send_message(message.from_user.id, 'CHOOSE interest hotel for you', reply_markup=markup_hotel)
    except (UnboundLocalError, KeyError):  # Срабатывает если по каким-то параметрам невозможно найти отели
        bot.send_message(message.from_user.id, "Please retry your request.")
        bot.delete_state(message.from_user.id)

    bot.delete_message(message.from_user.id, msg.message_id)


def hotels_detals(message: Message):
    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:

        propertyId = data['hotel_id']
        quanyity_pic = data['quantity_pic']
        distanceFromCenter = data['distanceFromCenter']
        if data['command'] == 'bestdeal' and data['measurement'] == 'kilometer':
            distanceFromCenter *= 1.61
            measurement = data['measurement']
        else:
            measurement = 'mile'
        cost_per_night = data['cost_per_night']
        total_cost = data['total_cost']
        rent_days = data['rent_days']


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
    hotel_id = str(data['hotel_id'])
    hotel_URL = f'https://www.hotels.com/h{hotel_id}.Hotel-Information'

    if quanyity_pic > 0:  # срабатывет, если количество фотографий больше нуля
        for i_ind, i_image in enumerate(photos):
            if int(i_ind) == int(quanyity_pic):
                break
            image_url: str = i_image["image"]["url"]
            medias.append(types.InputMediaPhoto(image_url))
        msg = bot.send_message(message.from_user.id, "Loading...")
        bot.send_media_group(chat_id=message.from_user.id, media=medias)
        bot.send_message(message.from_user.id, f"{quanyity_pic} pictures of hotel {hotel_name}: ")
        bot.delete_message(message.from_user.id, msg.message_id)

    bot.send_message(message.from_user.id, f"Short information about this hotel: \n"
                                           f"---------------------------------------------\n"
                                           f"Hotel's name: {hotel_name} \n"
                                           f"Address: {address} \n"
                                           f"link for hotel: {hotel_URL} \n"
                                           f"Distance from center: {round(distanceFromCenter, 2)} {measurement}\n"
                                           f"You are planning to rent for {rent_days} nights\n"
                                           f"Cost per night: {cost_per_night} USD\n"
                                           f"Total cost for all rent: {total_cost} USD")

    with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
        data["photos"] = medias
        data['hotel_name'] = hotel_name
        data['address'] = address

    bot.set_state(message.from_user.id, HotelInfoState.result)


def table_age(message: Message) -> None:  # Создаёт таблицу для выбора возраста ребёнка от 0 до 18
    markup = types.InlineKeyboardMarkup(row_width=3)
    for j_age in range(0, 18, 3):
        item_kid_age_1 = types.InlineKeyboardButton(f"{j_age}", callback_data=str(j_age))
        item_kid_age_2 = types.InlineKeyboardButton(f"{j_age+1}", callback_data=str(j_age+1))
        item_kid_age_3 = types.InlineKeyboardButton(f"{j_age+2}", callback_data=str(j_age+2))
        markup.add(item_kid_age_1, item_kid_age_2, item_kid_age_3)
    bot.send_message(message.from_user.id, "Now tell me how old they are: ", reply_markup=markup)


def choose_need_pic(message: Message) -> None:
    markup = types.InlineKeyboardMarkup(row_width=5)
    for i in range(1, 11, 5):
        item_1 = types.InlineKeyboardButton(f"{i}", callback_data=f'{i}')
        item_2 = types.InlineKeyboardButton(f"{i+1}", callback_data=f'{i+1}')
        item_3 = types.InlineKeyboardButton(f"{i+2}", callback_data=f'{i+2}')
        item_4 = types.InlineKeyboardButton(f"{i+3}", callback_data=f'{i+3}')
        item_5 = types.InlineKeyboardButton(f"{i+4}", callback_data=f'{i+4}')
        markup.add(item_1, item_2, item_3, item_4, item_5)
    item_0 = types.InlineKeyboardButton("Without photos", callback_data='0')
    markup.add(item_0)
    bot.send_message(message.from_user.id, "How many PHOTOS of the hotel would you like to see? ", reply_markup=markup)
    bot.set_state(message.from_user.id, HotelInfoState.quantity_pic)

def sql_input(user_id, db_data):
    with sqlite3.connect(user_id + '.db') as history_sql:  # создание и заполнение базы данных для History
        cursor = history_sql.cursor()
        query_db = " CREATE TABLE IF NOT EXISTS search_history " \
                   "(command_time TEXT, command TEXT, location_name TEXT, found_hotels TEXT, " \
                   "hotel_info TEXT, cost_per_night TEXT, rent_days TEXT) "
        cursor.execute(query_db)
        cursor.execute(" INSERT INTO search_history VALUES(?, ?, ?, ?, ?, ?, ?);", db_data)

    history_sql.commit()

def sql_output():
    user_id = str(message.from_user.id)
    try:
        with sqlite3.connect(user_id + '.db') as history_sql:
            cursor = history_sql.cursor()
            cursor.execute("SELECT * from search_history")
            records = cursor.fetchall()
            bot.send_message(message.from_user.id, "History of your search: ")
            for row in records:
                bot.send_message(message.from_user.id, "___________________________________________ \n"
                                                       f"Command time: {row[0]} \n"
                                                       f"Command: {row[1]} \n"
                                                       f"Location name: {row[2]} \n"
                                                       f"\n"
                                                       f"Found hotels: \n{row[3]} \n"
                                                       f"Hotel info: {row[4]} \n"
                                                       f"Cost per night: {row[5]} USD \n"
                                                       f"Quantity night: {row[6]}")
            cursor.close()
    except sqlite3.Error as error:
        bot.send_message(message.from_user.id, f"Your search history is empty.")