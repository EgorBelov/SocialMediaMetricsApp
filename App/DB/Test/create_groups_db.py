import psycopg2

import request_groups

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    database="SocialMediaMetrics",
    user="postgres",
    password="123321",
    host="localhost",
    port="5432"
)

# Создание курсора
cursor = conn.cursor()

# Создание таблицы, если ее еще нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vk_groups (
        id SERIAL PRIMARY KEY,
        id_vk BIGINT,
        name VARCHAR(50),
        count_sub INTEGER
    )
''')
conn.commit()

# Вставка данных в таблицу
for group in request_groups.request_groups():
    cursor.execute('''
        INSERT INTO vk_groups (id_vk, name)
        VALUES (%s, %s)
    ''', (group['id'], group['name']))

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()
