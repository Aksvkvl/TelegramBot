# main telegrambot code
import sqlite3
from datetime import datetime
import telebot
from telebot import types
import uuid
import SQL_logic
from classes import MessageButtons
bot = telebot.TeleBot('5973753178:AAG_niAMb03lkp-U4eMDkP1TDzG-Ifh2UpA')

conn = sqlite3.connect('EasyConstruction.db')
c = conn.cursor()

states = {}
client_id = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    # Создайте экземпляр класса MessageButtons
    message_buttons = MessageButtons(message.chat.id, bot, types)

    # Определите текст и кнопки для отправки
    text = 'Привет! Я помогу организовать работу. Для начала, пожалуйста, выберите свою роль:'
    buttons = [
        ("Клиент", "client", "/client"),
        ("Исполнитель", "builders", "/builders")
    ]

    # Используйте экземпляр класса для отправки сообщения с кнопками
    message_buttons.send(text, buttons)

    # "Технадзор - нажмите /technical_inspector," "Поставщик - нажмите /supplier "
    # "соответственно.")


@bot.message_handler(commands=['client'])
def client(message):
    global states, client_id
    states[message.chat.id] = "clients"
    bot.send_message(message.chat.id,
                     "Отлично! Вы выбрали раздел клиента! Теперь вы можете просмотреть свои проекты" "по команде "
                     "/my_projects или создать новый проект по команде /new_project")


@bot.message_handler(commands=['contractor'])
def contractor(message):
    states[message.chat.id] = "builders"
    client_id[message.chat.id] = message.chat.id
    bot.send_message(message.chat.id, "Добро пожаловать в EasyConstruction! Теперь вы можете сформировать свой прайс "
                                      "/builder_default_price "
                                      "просматривать ваши действующие проекты /builder_projects")


@bot.message_handler(commands=['builder_projects'])
def builder_projects(message):
    client_id[message.chat.id] = message.chat.id
    bot.send_message(message.chat.id, "Здесь можно добавить свои выполненные объекты для того, "
                                      "чтобы сформировался средний прайс ваших цен\n"
                                      "Для добавления вашего проекта /builder_new_project\n"
                                      "Для изменения вашего проекта /builder_edit_project\n"
                                      "Для удаления вашего проекта /builder_delete_project\n"
                                      "Для просмотра вашего проекта /builder_view_project\n")


@bot.message_handler(commands=['builder_new_project'])
def builder_new_project(message):
    builder_id_input = message.chat.id
    bot.send_message(builder_id_input, "Введите имя проекта:")
    bot.register_next_step_handler(message, builder_project_name_handler, builder_id_input)


def builder_project_name_handler(message, builder_id_input):
    def generate_project_id():
        project_id = str(uuid.uuid4()).replace("-", "")[:256]
        return project_id

    project_name_input = message.text
    current_date = datetime.now().strftime("%Y-%m-%d")
    project_id = generate_project_id()
    conn = sqlite3.connect('EasyConstruction.db')
    c = conn.cursor()
    c.execute("INSERT INTO builders(client_id, project_id, project_name, created_date, updated_date) VALUES(?,?,?,?,?)",
              (builder_id_input, project_id, project_name_input, current_date, current_date))
    conn.commit()
    conn.close()
    bot.send_message(builder_id_input, "Вы создали проект " + project_name_input + ". Теперь вы можете просматривать "
                                                                                   "свои проекты "
                                                                                   "/builder_price_view_project")


@bot.message_handler(commands=['new_project'])
def new_project(message):
    client_id_input = message.chat.id
    bot.send_message(client_id_input, "Введите имя проекта:")
    bot.register_next_step_handler(message, builder_project_name_handler, client_id_input)


def project_name_handler(message, client_id_input):
    def generate_project_id():
        project_id = str(uuid.uuid4()).replace("-", "")[:256]
        return project_id

    project_name_input = message.text
    current_date = datetime.now().strftime("%Y-%m-%d")
    project_id = generate_project_id()
    conn = sqlite3.connect('EasyConstruction.db')
    c = conn.cursor()

    c.execute("INSERT INTO clients(client_id, project_id, project_name, created_date, updated_date) VALUES(?,?,?,?,?)",
              (client_id_input, project_id, project_name_input, current_date, current_date))

    conn.commit()
    conn.close()
    bot.send_message(client_id_input, "Вы создали проект " + project_name_input + ". Теперь вы можете просматривать "
                                                                                  "свои проекты " "/my_projects")


@bot.message_handler(commands=['my_projects'])
def my_projects(message):
    client_id = message.chat.id

    conn = sqlite3.connect('EasyConstruction.db')
    cursor = conn.cursor()

    cursor.execute("SELECT project_id, project_name FROM clients WHERE client_id=?", (client_id,))
    projects_list = cursor.fetchall()

    if len(projects_list) == 0:
        bot.send_message(client_id, "Список проектов пуст! Создайте новый /new_project")
    else:
        bot.send_message(client_id, "Чтобы перейти в проект нажмите на project_id, который находится ниже "
                                    "названия\nИли создать новый проект  /new_project\nВаши проекты:")

        for project_id, project_name in projects_list:
            project_link = f"{project_name}\n/{project_id}"
            bot.send_message(client_id, project_link)

            commands = f"project_{project_id}"

    cursor.close()
    conn.close()


headers = []  # глобальная переменная
column_name = ''  # глобальная переменная
new_value = None  # или другое значение по умолчанию


@bot.message_handler(commands=['123'])
def get_project_id(message):
    global current_project_id
    if current_project_id is not None:
        bot.send_message(message.chat.id, "Проект не выбран. Пожалуйста выберите проект или создайте новый "
                                          "/new_project /my_projects")
    else:
        current_project_id = message.text[1:]


@bot.callback_query_handler(func=lambda call: call.data in headers)
def edit_value(call):
    global column_name
    column_name = call.data

    markup = types.ForceReply(selective=False)
    bot.send_message(call.message.chat.id, f"Введите новое значение для столбца '{column_name}':", reply_markup=markup)
    bot.register_next_step_handler(call.message, save_value)


def save_value(message):
    new_value = message.text.strip()

    # Проверяем, что значение было изменено
    if new_value != "":
        # Добавьте здесь код для сохранения нового значения в нужном месте
        # Например, можно сохранить его в базу данных или в переменную
        # Обновляем значение ячейки в базе данных
        conn = sqlite3.connect('EasyConstruction.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE clients SET {column_name}=? WHERE project_id=?", (new_value, current_project_id))
        conn.commit()
        cursor.close()
        conn.close()

        bot.send_message(message.chat.id, "Значение успешно изменено\nВернуться к списку проектов "
                                          "/my_projects\nРедактировать данные проекта /edit_project")


# Счетчик вопросов
current_index = 0
column = None

data_tuple = SQL_logic.create_tuple_from_column()


# В функции push_project используйте data_tuple для сортировки по колонке queue
@bot.message_handler(commands=['push_project'])
def push_project(message):
    global current_index
    global column

    # Сортируем данные по номеру вопроса
    sorted_data = sorted(data_tuple, key=lambda x: x[0])
    print(sorted_data)

    if len(sorted_data) > current_index:

        question = sorted_data[current_index][1]  # Получаем значение из кортежа
        column = sorted_data[current_index][2]  # Получаем значение из командновона

        # Отправляем вопрос пользователю
        bot.send_message(chat_id=message.chat.id, text=question)

        # Регистрируем handler для обработки ответа
        bot.register_next_step_handler(message, process_answer, column, current_project_id)

        # Увеличиваем счетчик вопросов
        current_index += 1

    else:
        # current_index = 0
        bot.send_message(chat_id=message.chat.id, text=f"Вопросы закончились. Теперь вы можете перейти к текущему "
                                                       f"проекту \n/project_data \nили к остальным своим "
                                                       f"проектам\n/my_projects")


def process_answer(message, column, current_project_id):
    # Получаем ответ от пользователя
    answer = message.text

    # Обновляем данные в БД
    update_db(column, answer, current_project_id)

    # Переходим к следующему вопросу
    push_project(message)


def update_db(column, answer, current_project_id):
    # Подключаемся к БД
    connection = sqlite3.connect('EasyConstruction.db')

    cursor = connection.cursor()

    # Обновляем данные
    try:
        cursor.execute(f"UPDATE clients SET {column} = ? WHERE project_id = ?", (answer, current_project_id))
        connection.commit()
    except sqlite3.Error as e:
        print('Ошибка при выполнении SQL-запроса:', e)

    connection.commit()

    connection.close()


@bot.message_handler(commands=['edit_project'])
def edit_project(message):
    global current_project_id
    project_id = current_project_id
    if project_id:
        conn = sqlite3.connect('EasyConstruction.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE project_id=?", (project_id,))
        project_data = cursor.fetchall()
        cursor.close()
        conn.close()

        if project_data:
            global headers  # объявляем переменную как глобальную
            exclude_columns = ['id', 'client_id', 'project_id', 'created_date', 'updated_date']
            headers = [description[0] for description in cursor.description if description[0] not in exclude_columns]
            markup = types.InlineKeyboardMarkup(row_width=3)
            buttons = [types.InlineKeyboardButton(text=header, callback_data=header) for header in headers]
            markup.add(*buttons)

            bot.send_message(message.chat.id,
                             f"Выберите столбец для редактирования или пройдите шаг за шагом каждую строку "
                             f"/push_project или вернитесь к списку проектов /my_projects",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Данные проекта не найдены")
    else:
        bot.send_message(message.chat.id, "Номер проекта не выбран из раздела edit_project")


@bot.message_handler(commands=['project_data'])
def project_data(message):
    global current_project_id
    project_id = current_project_id
    if project_id:
        conn = sqlite3.connect('EasyConstruction.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM clients WHERE project_id=?", (project_id,))
        project_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if project_data:
            headers = [description[0] for description in cursor.description]
            exclude_columns = ['id', 'client_id', 'project_id']
            data = '\n'.join(
                [f"{header}: {value}" for header, value in zip(headers, project_data) if header not in exclude_columns])
            bot.send_message(message.chat.id, f"Данные проекта (ID проекта: {project_id}):\n{data}\n"
                                              "\nСоздать новый проект /new_project \nРедактировать данные проекта "
                                              "/edit_project \nМожно пройти заново"
                                              "опрос /push_project \nИли удалить данный проект "
                                              "/delete_project\nВернуться к списку проектов /my_projects")
        else:
            bot.send_message(message.chat.id, "Данные проекта не найдены в разделе project_data")
    else:
        bot.send_message(message.chat.id, "Номер проекта не выбран из раздела project_data")


@bot.message_handler(commands=['delete_project'])
def delete_project(message):
    global current_project_id
    project_id = current_project_id
    if project_id:
        conn = sqlite3.connect('EasyConstruction.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE project_id=?", (project_id,))
        bot.send_message(message.chat.id, "Проект удален")
        conn.commit()
        conn.close()
    else:
        bot.send_message(message.chat.id, "Номер проекта не выбран")


@bot.message_handler(func=lambda message: message.text.startswith('/'))
def project_id(message):
    global current_project_id
    current_project_id = message.text[1:].replace('/', '')

    conn = sqlite3.connect('EasyConstruction.db')
    cursor = conn.cursor()

    cursor.execute("SELECT project_name FROM clients WHERE project_id=?", (current_project_id,))
    project_name = cursor.fetchone()
    cursor.close()
    conn.close()

    if project_name:
        project_name = project_name[0]
        bot.send_message(message.chat.id, f"Вы выбрали проект {project_name} (ID проекта: {current_project_id})" "\n"
                                          "Посмотрите данные проекта /project_data" "\nВы можете ввести заново все "
                                          "данные /push_project" "\nИли удалить проект используя команду "
                                          "/delete_project\nВернуться к списку проектов /my_projects")
    else:
        bot.send_message(message.chat.id, "Проект не найден из прожект ИД")


bot.polling()
