import telebot

# Replace 'BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot("5973753178:AAG_niAMb03lkp-U4eMDkP1TDzG-Ifh2UpA")


class MessageButtons:

    def __init__(self, chat_id, bot_instance, types_instance):
        self.chat_id = chat_id
        self.bot = bot_instance
        self.types = types_instance

    def send(self, text, buttons):
        button_command = ""  # Инициализируйте button_command здесь
        markup = self.types.InlineKeyboardMarkup()
        for button_text, button_callback, command in buttons:
            button = self.types.InlineKeyboardButton(text=button_text, callback_data=button_callback)
            markup.add(button)
            button_command = command  # Обновите button_command внутри цикла

        self.bot.send_message(self.chat_id, text=f"{text} {button_command}", reply_markup=markup)
