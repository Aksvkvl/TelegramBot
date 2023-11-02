# SQL logic module
import sqlite3


def create_tuple_from_column():
    connection = sqlite3.connect('EasyConstruction.db')
    cursor = connection.cursor()

    table_name = 'questions'

    # Получаем данные из колонок queue clientq и cols

    cursor.execute("SELECT queue, clientQ, cols FROM {}".format(table_name))
    result = cursor.fetchall()

    # Создаем кортеж из данных
    data_tuple = tuple((row[0], row[1], row[2]) for row in result)

    return data_tuple


def update_table(table_name):
    connection = sqlite3.connect('EasyConstruction.db')
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info({})".format(table_name))
    columns = [column[0] for column in cursor.fetchall()]

    # Получаем список названий столбцов из таблицы 'questions'
    cursor.execute("SELECT cols FROM questions")
    result = cursor.fetchall()

    # Проверяем, что результат не равен None
    if result:
        for row in result:
            columns_to_add = row[0].split(',')

            # Получаем список существующих столбцов в таблице
            cursor.execute("PRAGMA table_info({})".format(table_name))
            existing_columns = [column[1] for column in cursor.fetchall()]

            # Добавляем новые столбцы в таблицу, если они не существуют
            for column in columns_to_add:
                if column not in existing_columns:
                    cursor.execute("ALTER TABLE {} ADD COLUMN {}".format(table_name, column))

        # Сохраняем изменения в базе данных
        connection.commit()

    # Получаем список всех колонок с NULL значениями
    columns_with_null = []
    for column in columns:
        if column != f'{table_name}.user_id':
            cursor.execute("SELECT * FROM {} WHERE {} IS NULL".format(table_name, column))
            if cursor.fetchone():
                columns_with_null.append(column)

    # Удаляем столбцы с пустыми значениями
    for column in columns_with_null:
        try:
            cursor.execute("ALTER TABLE {} DROP COLUMN {}".format(table_name, column))
        except sqlite3.OperationalError:
            pass

    connection.close()


# Теперь вы можете вызвать эту функцию для 'clients' и 'builders'
update_table('clients')
update_table('builders')


def create_project(user_id, project_name):
    def generate_project_id():
        project_id = str(uuid.uuid4()).replace("-", "")[:256]
        return project_id

    current_date = datetime.now().strftime("%Y-%m-%d")
    project_id = generate_project_id()
    conn = sqlite3.connect('EasyConstruction.db')
    c = conn.cursor()

    # Определяем таблицу в зависимости от типа пользователя
    if user_id in builders:
        table_name = "builders"
    else:
        table_name = "clients"

    c.execute(f"INSERT INTO {table_name}(client_id, project_id, project_name, created_date, updated_date) VALUES(?,?,"
              f"?,?,?)",
              (user_id, project_id, project_name, current_date, current_date))
    conn.commit()
    conn.close()

    return project_name, project_id

