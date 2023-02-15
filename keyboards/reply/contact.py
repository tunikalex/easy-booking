from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def request_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Send your contact', request_contact=True))

    return keyboard