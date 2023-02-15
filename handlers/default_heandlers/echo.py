from telebot.types import Message
from loader import bot
from handlers.custom_heandlers import hello

# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(content_types=["text"], state=None)
def bot_echo(message: Message):
    if message.text == '/hello':
        hello.get_comm_hello(message=message)
    elif message.text.lower() in ['hello', 'hi', 'привет', 'ghbdtn', 'hello-world']:
        hello.get_text_hello(message=message)
    else:
        bot.reply_to(message, "It is echo without condition. \nMessege: "
                              f"{message.text}")
