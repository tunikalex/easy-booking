from telebot.handler_backends import State, StatesGroup


class HotelInfoState(StatesGroup):
    search_location = State()
    quantity_hotels = State()
    need_pic = State()
    quantity_pic = State()
    # output_info = State()
