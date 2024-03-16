import os

from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2

from App.DB.requests import request_count_likes_from_wall, request_users_get
from App.mutual_friends.create_graph import D3
from App.mutual_friends.settings import token, api_v, max_workers

app = Flask(__name__)


# Страница успешного создания базы данных
@app.route('/')
def index():
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


@app.route('/create_and_redirect/<int:user_id>')
def create_and_redirect(user_id):
    a = D3(token, user_id, api_v, max_workers)
    return render_template('create_graph.html')



if __name__ == '__main__':
    app.run(debug=True)
