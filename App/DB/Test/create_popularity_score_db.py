import psycopg2
import request_count_likes_from_photos
import time
import request_counts_friends_followers

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

# Добавление столбца popularity_score, если его еще нет
alter_query = "ALTER TABLE public.vk_users ADD COLUMN IF NOT EXISTS popularity_score real;"
cursor.execute(alter_query)
conn.commit()

# Выполнение запроса для получения данных из таблицы
cursor.execute(
    "SELECT id, avg_likes_on_photos, likes_on_wall, comments_on_wall, reposts_on_wall, count_friends, count_followers FROM public.vk_users")

# Извлечение данных
rows = cursor.fetchall()


# Определение функции цели
def calculate_popularity_score(params):
    avg_likes_on_photos, likes_on_wall, comments_on_wall, reposts_on_wall, count_friends, count_followers = params
    # Пример функции цели (веса параметров могут быть изменены)
    popularity_score = (
            0.2 * avg_likes_on_photos +
            0.3 * likes_on_wall +
            0.2 * comments_on_wall +
            0.2 * reposts_on_wall +
            0.1 * count_friends +
            0.1 * count_followers
    )
    return popularity_score


# Обновление записей в базе данных
for row in rows:
    user_id, avg_likes, likes, comments, reposts, friends, followers = row[0], row[1], row[2], row[3], row[4], row[5], \
    row[6]
    params = (avg_likes, likes, comments, reposts, friends, followers)

    # Вычисление функции цели
    score = calculate_popularity_score(params)

    # Обновление записи в базе данных
    update_query = f"UPDATE public.vk_users SET popularity_score = {score} WHERE id = {user_id}"
    cursor.execute(update_query)

# Подтверждение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()