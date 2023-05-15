import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Environment variables not loaded because .env file is missing')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Run a bot"),
    ('hello', 'Say hello, be polite'),
    ('help', "Display command help"),
    ('highprice', "Display the most EXPENSIVE hotels in the city"),
    ('lowprice', 'Display the CHEAPEST hotels in the city'),
    ('bestdeal', 'Еhe best offers for the given parameters'),
    ('history', 'View your search history')
        )
