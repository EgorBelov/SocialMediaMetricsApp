from flask import Flask, render_template, request, redirect, url_for
import psycopg2


from App.requests import request_users_get, request_count_likes_from_wall


app = Flask(__name__)

# Функция для создания соединения с базой данных
def create_db_connection():
    conn = psycopg2.connect(
        database="SocialMediaMetrics",
        user="postgres",
        password="123321",
        host="localhost",
        port="5432"
    )
    return conn

# Функция для создания таблицы vk_users
def create_vk_users_table(cursor):
    cursor.execute('DROP TABLE IF EXISTS vk_users')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vk_users (
            id SERIAL PRIMARY KEY,
            id_vk BIGINT,
            first_name VARCHAR(50),
            last_name VARCHAR(50)
        )
    ''')

# Функция для вставки данных в таблицу vk_users
def insert_data_into_vk_users(cursor, user_ids):
    for user in request_users_get.request_users_get(user_ids):
        if user['is_closed'] is False and user['is_no_index'] is False:
            cursor.execute('''
                INSERT INTO vk_users (id_vk, first_name, last_name)
                VALUES (%s, %s, %s)
            ''', (user['id'], user['first_name'], user['last_name']))

# Главная страница с формой для ввода ID пользователей
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_ids = request.form['user_ids']
        user_ids_list = user_ids.split(',')
        conn = create_db_connection()
        cursor = conn.cursor()
        create_vk_users_table(cursor)
        insert_data_into_vk_users(cursor, user_ids)
        conn.commit()
        cursor.close()
        conn.close()
        update_data()
        return redirect(url_for('view_data'))
    return render_template('index.html')




# Страница успешного создания базы данных
@app.route('/view_data')
def view_data():
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

    # Запрос на выбор всех пользователей из таблицы vk_users
    cursor.execute('SELECT * FROM vk_users')
    users_data = cursor.fetchall()

    # Сохранение изменений и закрытие соединения
    cursor.close()
    conn.close()

    return render_template('view_data.html', users_data=users_data)


# Новый маршрут для обновления данных после создания БД
@app.route('/update_data', methods=['GET'])
def update_data():
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
    for user_id in user_ids:
        metrics = request_count_likes_from_wall.request_count_likes_from_wall(user_id[0])
        cursor.execute('''
            UPDATE vk_users
            SET likes_on_wall = %s,
                reposts_on_wall = %s,
                comments_on_wall = %s
            WHERE id_vk = %s
        ''', (metrics[0], metrics[1], metrics[2], user_id[0]))

    # Сохранение изменений и закрытие соединения
    conn.commit()
    cursor.close()
    conn.close()

    return 'Данные успешно обновлены!'






if __name__ == '__main__':
    app.run(debug=True)
