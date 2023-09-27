from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import Dispatcher as AiogramDispatcher

bot = Bot(token="BOT_TOKEN")
dp = Dispatcher(bot)


class MessageButtons:

    def __init__(self, chat_id):
        self.chat_id = chat_id

    async def send(self, text, buttons):
        keyboard = []
        for button_text, button_callback, button_command in buttons:
            button = InlineKeyboardButton(button_text, callback_data=button_callback)
            keyboard.append([button])

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.send_message(self.chat_id, text=f"{text} {button_command}", reply_markup=reply_markup)
