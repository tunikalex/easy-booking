# Telegram bot for hotel search.
___
The Telegram bot is used to search for hotels around the world. The bot is written in **Python 3.10** and uses the modules described in requirements.txt file.
Also, to connect a bot, a bot generator is used [@BotFather](https://t.me/BotFather) and public API directory [RapidAPI.com](https://rapidapi.com/apidojo/api/hotels4) 

**Headings:**
- [Description of the team's work](#description)
- [Getting started](#getting-started)
- [Developing](#developing)
- [Database](#database)

Using special bot commands, the user can do the following:
1. Request information about the hotel starting with the cheapest (command /lowprice).
2. Request information about hotels starting with the most expensive (command /highprice).
3. Request information about hotels by price range (command /bestdeal).
4. Find out request history (command /history).

Without a running script, the bot does not respond to commands (or anything else).
___

## Description
### Comand /lowprice
After entering the command, the user is prompted:
- City (locality) in which hotels will be searched.
- Clarify the location by clicking on the suggested button.
- The number of hotels that will be offered to the user.
- Check-in date and check-out date. Selection in the calendar grid.
- Number of adults and number of children per room.
- The number of photographs of the hotel offered for your reference.
- Selecting a specific hotel from the list of proposed ones.
- Providing information about the hotel.
### Comand /highprice
After entering the command, the user is prompted:
- City (locality) in which hotels will be searched.
- Clarify the location by clicking on the suggested button.
- The number of hotels that will be offered to the user.
- Check-in date and check-out date. Selection in the calendar grid.
- Number of adults and number of children per room.
- The number of photographs of the hotel offered for your reference.
- Selecting a specific hotel from the list of proposed ones.
- Providing information about the hotel.
### Comand /bestdeal
After entering the command, the user is prompted:
- City (locality) in which hotels will be searched.
- Clarify the location by clicking on the suggested button.
- Enter a range of rental prices in US dollars per night.
- Selecting a distance measurement system. Kilometers or miles.
- Enter the distance from the center where you should search for hotels.
- The number of hotels that will be offered to the user.
- Check-in date and check-out date. Selection in the calendar grid.
- Number of adults and number of children per room.
- The number of photographs of the hotel offered for your reference.
- Selecting a specific hotel from the list of proposed ones.
- Providing information about the hotel.

### Comand /history
After entering the command, a brief history of the user's requests is displayed.
- The last three.
- The last five.
- For today.
- The whole story.
___

## Getting started
1. Install the virtual environment in the project directory and change the file name "example.env" to ".env". 
File .env must contain a token and API-key. <br>
***BOT_TOKEN*** you need to get it in the telegram bot for generating bots[@BotFather](https://t.me/BotFather). <br>
***RAPID_API_KEY*** Telegram bot is used to search for hotels around the world. The bot is written in **Python 3.10**, and uses the modules described in the requirements.txt file.
Get it on the website*** [RapidAPI.com](https://rapidapi.com/apidojo/api/hotels4) on the page Hotels4 (*Header Parameters: X-RapidAPI-Key*).

    ```
        BOT_TOKEN='your token'
        RAPID_API_KEY='your key'
    ```
2. Add the required packages from the requirements.txt file. To do this, in the terminal you need to run:   
    ```
      pip install -r requirements.txt
   ```
    If you ever need to remove a module for any reason, use the same command but with the uninstall keyword instead of install.


3. Проект запускается заглавным файлом **<u>main.py</u>**.
___

## Developing
Technologies used:
- Pithon 3.10
- venv, python-dotenv 
- python-telegram-bot-calendar
- pyTelegramBotAPI
- SQLite3
- json
___

## Database
A database for storing hotel search history has been implemented **SQLite3** and its functions are in the repository ./custom_heandlers/functions.py.  
Function **sql_input** - for loading into the database and **sql_output** to extract data from the database.
