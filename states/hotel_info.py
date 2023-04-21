from telebot.handler_backends import State, StatesGroup


class HotelInfoState(StatesGroup):
    search_location = State()
    price_min = State()
    price_max = State()
    check_in = State()
    check_out = State()
    measurements = State()
    distance_min = State()
    distance_max = State()
    room = State()
    adults = State()
    kids = State()
    amount_children = State()
    kids_age = State()
    need_pic = State()
    quantity_pic = State()
    result = State()