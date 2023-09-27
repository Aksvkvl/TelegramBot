import sqlite3
import uuid
from datetime import datetime
import telebot
from telebot import types
from SQL_logic import create_tuple_from_column

bot = telebot.TeleBot('5973753178:AAE42A74HzuaSOOsu9OQlivz-sBtH7ABUkI')

conn = sqlite3.connect('EasyConstruction.db')

