import telebot


class MessageButtons:

    def __init__(self, chat_id, bot_instance, types_instance):
        ...

    def send(self, text, buttons):
        markup = self.types.ReplyKeyboardMarkup(resize_keyboard=True)

        for button_text, _, command in buttons:
            button = self.types.KeyboardButton(text=button_text, command=command)
            markup.add(button)

        self.bot.send_message(self.chat_id, text, reply_markup=markup)