import psycopg2
import request_count_likes_from_wall

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

# Добавление столбца avg_likes в таблицу vk_users
cursor.execute('ALTER TABLE vk_users ADD COLUMN likes_on_wall INTEGER')
cursor.execute('ALTER TABLE vk_users ADD COLUMN comments_on_wall INTEGER')
cursor.execute('ALTER TABLE vk_users ADD COLUMN reposts_on_wall INTEGER')


# Запрос на выбор всех пользователей из таблицы vk_users
cursor.execute('SELECT id_vk FROM vk_users')
user_ids = cursor.fetchall()

# Обновление данных в таблице средним количеством лайков на фото
for i, user_id in enumerate(user_ids):
    metrics = request_count_likes_from_wall.request_count_likes_from_wall(user_id[0])  # user_id[0] - извлечение первого элемента кортежа
    cursor.execute('''
        UPDATE vk_users
        SET likes_on_wall = %s,
            reposts_on_wall = %s,
            comments_on_wall = %s 
        WHERE id_vk = %s
    ''', (metrics[0], metrics[1], metrics[2], user_id[0]))

    # # Добавить задержку каждые 10 запросов
    # if (i + 1) % 8 == 0:
    #     time.sleep(5)

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()