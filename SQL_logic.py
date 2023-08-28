import sqlite3


def create_tuple_from_column(column):
    connection = sqlite3.connect('EasyConstruction.db')
    cursor = connection.cursor()

    table_name = 'questions'

    # Получаем данные из колонки
    cursor.execute("SELECT {} FROM {}".format(column, table_name))
    result = cursor.fetchall()

    # Создаем кортеж из данных
    data_tuple = tuple(row[0] for row in result)

    return data_tuple


connection = sqlite3.connect('EasyConstruction.db')
cursor = connection.cursor()

table_name = 'clients'

cursor.execute("PRAGMA table_info(clients)", {'clients': table_name})
columns = [column[0] for column in cursor.fetchall()]

# Получаем список названий столбцов из таблицы 'questions'

table_name = 'questions'

cursor.execute("SELECT columns FROM questions")
result = cursor.fetchall()

# Проверяем, что результат не равен None
if result:
    for row in result:
        columns_to_add = row[0].split(',')

        # Получаем список существующих столбцов в таблице 'clients'
        cursor.execute("PRAGMA table_info(clients)", {'clients': table_name})
        existing_columns = [column[1] for column in cursor.fetchall()]

        # Добавляем новые столбцы в таблицу 'clients', если они не существуют
        for column in columns_to_add:
            if column not in existing_columns:
                cursor.execute("ALTER TABLE {} ADD COLUMN {}".format(table_name, column))

    # Сохраняем изменения в базе данных
    connection.commit()

# Получаем список всех колонок с NULL значениями
columns_with_null = []
for column in columns:
    if column != 'clients.user_id':
        cursor.execute("SELECT * FROM {} WHERE {} IS NULL".format(table_name, column))
        if cursor.fetchone():
            columns_with_null.append(column)

# Удаляем столбцы с пустыми значениями
for column in columns_with_null:
    try:
        cursor.execute("ALTER TABLE {} DROP COLUMN {}".format(table_name, column))
    except sqlite3.OperationalError:
        pass

# Создаем кортеж из колонки 'clientQ'
clientQ_tuple = create_tuple_from_column('clientQ')

# Выводим созданный кортеж
print(clientQ_tuple)

# Сохраняем изменения в базе данных
connection.commit()
