from telebot.types import Message
from loader import bot

@bot.message_handler(commands=['hello'])
def get_comm_hello(message: Message) -> None:
    print('hello')
    bot.send_message(message.from_user.id, f"Hello, {message.from_user.username}! I absolutely happy to see you!")


@bot.message_handler(content_types=['text'])
def get_text_hello(message: Message) -> None:
    if message.text.lower() in ('hello', 'hi', 'привет', 'ghbdtn', 'hello-world'):
        bot.send_message(message.from_user.id, f"Hello, {message.from_user.username}, nice to meet you!",)