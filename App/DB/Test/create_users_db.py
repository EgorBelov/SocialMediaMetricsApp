import psycopg2
import request_users
import request_users_get

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

# Удаление таблицы, если она существует
cursor.execute('DROP TABLE IF EXISTS vk_users')

# Создание таблицы, если ее еще нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vk_users (
        id SERIAL PRIMARY KEY,
        id_vk BIGINT,
        first_name VARCHAR(50),
        last_name VARCHAR(50)
    )
''')
conn.commit()

# # Вставка данных в таблицу
# for user in request_users.request_users():
#     if user['is_closed'] is False and user['is_no_index'] is False:
#         cursor.execute('''
#             INSERT INTO vk_users (id_vk, first_name, last_name)
#             VALUES (%s, %s, %s)
#         ''', (user['id'], user['first_name'], user['last_name']))

user_ids = ['16257176', '181260570', '84006516', '475885221','181507171','557450182', '131850969','486363517','181273806' ]

# Вставка данных в таблицу
for user in request_users_get.request_users_get(user_ids):
    if user['is_closed'] is False and user['is_no_index'] is False:
        cursor.execute('''
            INSERT INTO vk_users (id_vk, first_name, last_name)
            VALUES (%s, %s, %s)
        ''', (user['id'], user['first_name'], user['last_name']))



# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()
