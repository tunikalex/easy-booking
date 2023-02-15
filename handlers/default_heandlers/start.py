from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Hello, {message.from_user.full_name}! Nice to meet you! \n"
                          f"Travel bot started work. \n"
                          f"To do the first steps, you can use the /help command")
