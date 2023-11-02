# Модуль строителя для Main.py
# Code snippet for Main.py
import sqlite3
import uuid

current_project_id = {}


# Приветствие ддля раздела строителей
def greeting_contractor(message):
    return "Добро пожаловать в EasyConstruction! Теперь вы можете сформировать свой прайс /builder_price " \
           "просматривать ваши действующие проекты /builder_projects"


# Раздел работы с прайсами
def builder_projects(message):
    message.reply_text("Здесь можно добавить свои выполненные объекты для того, "
                       "чтобы сформировался средний прайс ваших цен"
                       "Для добавления вашего проекта /builder_price_add_project"
                       "Для изменения вашего проекта /builder_price_edit_project"
                       "Для удаления вашего проекта /builder_price_delete_project"
                       "Для просмотра вашего проекта /builder_price_view_project"
                       "Для отмены используйте /cancel")
    return message


# функция для команды /builder_price_add_project
def builder_price_add_project(message):
    project_id = str(uuid.uuid4().int)[:16]  # Генерация нового project_id с помощью модуля uuid
    project_name = message.text  # Получение названия проекта от пользователя

    # Получение текущего пользователя
    user_id = message.from_user.id

    # Подключение к базе данных
    connection = sqlite3.connect("EasyConstruction.db")

    # Создание объекта курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    # Создание новой строки в таблице builders с указанием user_id
    insert_query = "INSERT INTO builders (project_id, project_name, user_id) VALUES (?, ?, ?)"
    values = (project_id, project_name, user_id)
    cursor.execute(insert_query, values)

    # Подтверждение изменений в базе данных
    connection.commit()

    # Закрытие соединения с базой данных
    cursor.close()
    connection.close()

    response_text = (f"Проект {project_name} успешно создан с project_id: {project_id}. "
                     f"Теперь вы можете просмотреть все ваши проекты /builder_price_view_project")
    message.reply_text(response_text)


def view_builder_project(message):
    # Получение текущего пользователя
    user_id = message.from_user.id

    # Подключение к базе данных
    connection = sqlite3.connect("EasyConstruction.db")

    # Создание объекта курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    # Выполнение SQL-запроса с фильтром по пользователю
    cursor.execute("SELECT project_id, project_Name FROM builders WHERE user_id=?", (user_id,))

    # Получение результатов запроса
    results = cursor.fetchall()

    # Завершение запроса и закрытие соединения
    cursor.close()
    connection.close()

    # Вывод результатов запроса
    response_text = ""
    for row in results:
        project_id = row[0]
        project_name = row[1]
        response_text += f"project_id: /{project_id}\n"
        response_text += f"project_Name: {project_name}\n\n"

    message.reply_text(response_text)


def builder_select_project(message):
    # Получение выбранного project_id из сообщения пользователя
    selected_project_id = message.text.split('/')[1]

    # Присвоение выбранного project_id глобальной переменной current_project_id
    global current_project_id
    current_project_id = selected_project_id

    # Вывод сообщения пользователю
    response_text = "Вы можете сделать:\n"
    response_text += "1. Посмотреть информацию о проекте /builder_project_data\n"
    response_text += "2. Изменить информацию о проекте /edit_builder_project\n"
    response_text += "3. Удалить проект /delete_builder_project\n"

    message.reply_text(response_text)


def builder_project_data(message):
    # Получение выбранного проекта project_id из переменной current_project_id
    project_id = current_project_id

    # Подключение к базе данных
    connection = sqlite3.connect("EasyConstruction.db")

    # Создание объекта курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    # Выполнение запроса с фильтром по project_id
    cursor.execute("SELECT * FROM builders WHERE project_id=?", (project_id,))

    # Получение результатов запроса
    results = "Здесь вы можете отредактировать данные проекта:", {current_project_id}
    # в inline-кнопках
    results += cursor.fetchall()

    # Отправка пользователю содержимого проекта
    message.reply_text(results)


def edit_builder_project(message):
    # Получение выбраннопроека project_id из переменновой current_project_id
    project_id = current_project_id

    # Подключение к базе данных
    connection = sqlite3.connect("EasyConstruction.db")

    # Создание курсора для выполнения SQL-запросов
    cursor = connection.cursor()

    # Выполнение запроса с фильтром по пользователю
    cursor.execute("SELECT * FROM builders WHERE project_id=?", (project_id,))
