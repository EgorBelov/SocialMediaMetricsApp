import psycopg2
import request_count_likes_from_photos
import time

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
cursor.execute('ALTER TABLE vk_users ADD COLUMN avg_likes_on_photos REAL')

# Запрос на выбор всех пользователей из таблицы vk_users
cursor.execute('SELECT id_vk FROM vk_users')
user_ids = cursor.fetchall()

# Обновление данных в таблице средним количеством лайков на фото
for i, user_id in enumerate(user_ids):
    avg_likes = request_count_likes_from_photos.request_count_likes_from_photos(user_id[0])  # user_id[0] - извлечение первого элемента кортежа
    cursor.execute('''
        UPDATE vk_users
        SET avg_likes_on_photos = %s
        WHERE id_vk = %s
    ''', (avg_likes, user_id[0]))

    # Добавить задержку каждые 10 запросов
    if (i + 1) % 8 == 0:
        time.sleep(5)

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()