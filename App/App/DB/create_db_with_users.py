import psycopg2
from requests_api_VK.request_count_likes_from_wall import request_count_likes_from_wall
from requests_api_VK.request_users_get import request_users_get
from requests_api_VK.request_count_followers import request_count_followers
from requests_api_VK.request_count_friends import request_count_friends

conn = psycopg2.connect(
    database="SocialMediaMetrics",
    user="postgre_serv",
    password="123321",
    host="80.87.201.50",
    port="38147"
)

# Создание курсора
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS vk_users')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vk_users (
        id SERIAL PRIMARY KEY,
        id_vk BIGINT,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        count_friends INTEGER,
        count_followers INTEGER,
        likes_on_wall INTEGER,
        comments_on_wall INTEGER, 
        reposts_on_wall INTEGER, 
        count_posts_on_wall INTEGER,
        сonnectivity BOOLEAN,
        diameter INTEGER,
        radius INTEGER,
        page_rank FLOAT,
        betweenness_centrality FLOAT,
        degree_centrality FLOAT,
        transitivity FLOAT,
        assortativity FLOAT,
        clustering_coefficient FLOAT
    )
''')


# Открываем файл для чтения
with open('users_uids', 'r') as file:
    # Считываем строки из файла и удаляем лишние пробелы и символы новой строки
    user_ids = [line.strip() for line in file.readlines()]

users = request_users_get(user_ids)

for user in users:
    if user['is_closed'] is False and user['is_no_index'] is False:
        cursor.execute('''
            INSERT INTO vk_users (id_vk, first_name, last_name)
            VALUES (%s, %s, %s)
        ''', (user['id'], user['first_name'], user['last_name']))

cursor.execute('SELECT * FROM vk_users')
users_ids = cursor.fetchall()


# Обновление данных в таблице средним количеством лайков на фото
for user_id in users_ids:
    metrics = request_count_likes_from_wall(user_id[1])
    cursor.execute('''
        UPDATE vk_users
        SET likes_on_wall = %s,
            reposts_on_wall = %s,
            comments_on_wall = %s,
            count_posts_on_wall = %s
        WHERE id_vk = %s
    ''', (metrics[0], metrics[1], metrics[2], metrics[3], user_id[1]))

    count = request_count_friends(user_id[1])
    cursor.execute('''
            UPDATE vk_users
            SET count_friends = %s
            WHERE id_vk = %s
        ''', (count, user_id[1]))
    count = request_count_followers(user_id[1])
    cursor.execute('''
                UPDATE vk_users
                SET count_followers = %s
                WHERE id_vk = %s
            ''', (count, user_id[1]))

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()