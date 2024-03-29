import sqlite3
from datetime import datetime
import uuid
import aiogram
from SQL_logic import create_tuple_from_column

def client(message):
    states[message.chat.id] = "client"
    client_id[message.chat.id] = message.chat.id
    bot.send_message(message.chat.id,
                     "Отлично! Вы выбрали раздел клиента! Теперь вы можете просмотреть свои проекты" "по команде "
                     "/my_projects или создать новый проект по команде /new_project")


def new_project(message):
    client_id_input = message.chat.id
    bot.send_message(client_id_input, "Введите имя проекта:")
    bot.register_next_step_handler(message, project_name_handler, client_id_input)


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


def get_project_id(message):
    global current_project_id
    if current_project_id is not None:
        bot.send_message(message.chat.id, "Проект не выбран. Пожалуйста выберите проект или создайте новый "
                                          "/new_project /my_projects")
    else:
        current_project_id = message.text[1:]


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


@bot.message_handler(commands=['push_project'])
def push_project(message):
    global current_index
    global column

    # Получаем данные
    data = create_tuple_from_column('cols', 'clientq')

    # Сортируем данные по номеру вопроса
    sorted_data = sorted(data, key=lambda x: int(x.split(':')[0]))

    if len(sorted_data) > current_index:

        # Получаем текущий вопрос
        question = sorted_data[current_index]
        column = sorted_data[current_index].split(':')[1]

        # Отправляем вопрос пользователю
        bot.send_message(chat_id=message.chat.id, text=question)

        # Регистрируем handler для обработки ответа
        bot.register_next_step_handler(message, process_answer, column, current_project_id)

        # Увеличиваем счетчик вопросов
        current_index += 1

    else:
        current_index = 0
        bot.send_message(chat_id=message.chat.id, text="Вопросы закончились. Теперь вы можете перейти к своим проектам "
                                                       "/my_projects")


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
        bot.send_message(message.chat.id, "Проект не найден")