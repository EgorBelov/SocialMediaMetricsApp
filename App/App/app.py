import base64
import io
import os
import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
from matplotlib import pyplot as plt

from mutual_friends.create_graph import D3
from mutual_friends.settings import token, api_v, max_workers

app = Flask(__name__)


# Страница успешного создания базы данных
@app.route('/')
def index():
    # Подключение к базе данных PostgreSQL
    conn = psycopg2.connect(
        database="SocialMediaMetrics",
        user="postgre_serv",
        password="123321",
        host="80.87.201.50",
        port="38147"
    )

    # Создание курсора
    cursor = conn.cursor()

    # Запрос на выбор всех пользователей из таблицы vk_users
    cursor.execute('SELECT * FROM vk_users')
    users_data = cursor.fetchall()
    user_names = []
    pagerank_data = []
    betweennesscentrality_data = []
    degreecentrality_data = []
    transitivity_data = []
    assortativity_data = []
    clusteringcoefficient_data = []
    for user in users_data:
        user_names.append(str(user[2]) + ' ' + str(user[3]))
        pagerank_data.append(user[13])
        betweennesscentrality_data.append(user[14])
        degreecentrality_data.append(user[15])
        transitivity_data.append(user[16])
        assortativity_data.append(user[17])
        clusteringcoefficient_data.append(user[18])

    # pagerank_graph = create_graph(user_names, pagerank_data, 'pagerank')
    # betweennesscentrality_graph = create_graph(user_names, betweennesscentrality_data, 'betweennesscentrality')
    # degreecentrality_graph = create_graph(user_names, degreecentrality_data, 'degreecentrality')
    # transitivity_graph = create_graph(user_names, transitivity_data, 'transitivity')
    # assortativity_graph = create_graph(user_names, pagerank_data, 'assortativity')
    # clusteringcoefficient_graph = create_graph(user_names, clusteringcoefficient_data, 'clusteringcoefficient')
    graphs = []
    # Добавляем каждый график в слайдер
    # graphs = [pagerank_graph, betweennesscentrality_graph, degreecentrality_graph, transitivity_graph,
    #           assortativity_graph, clusteringcoefficient_graph]
    # Сохранение изменений и закрытие соединения
    cursor.close()
    conn.close()

    return render_template('index.html', users_data=users_data,
                           graphs = graphs)


@app.route('/create_and_redirect/<int:user_id>')
def create_and_redirect(user_id):
    a = D3(token, user_id, api_v, max_workers)
    return render_template('create_graph.html')



# Функция для создания графика и сохранения его как изображения
def create_graph1(user_names, metric_data, metric_name):
    fig = go.Figure()
    # Создаем график на основе метрики данных
    fig.add_trace(go.Bar(x=user_names, y=metric_data))
    fig.update_layout(title_text=metric_name, xaxis_title="Имя и Фамилия", yaxis_title="Значение метрики")
    # Кодируем изображение в base64
    image_png = fig.to_image(format="png")
    return image_png

def create_graph(user_names, metric_data, metric_name):
    fig, ax = plt.subplots()
    ax.bar(user_names, metric_data)
    ax.set_title(metric_name)
    ax.set_xlabel('Имя и Фамилия')
    ax.set_ylabel('Значение метрики')
    # Save the plot as a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the image to base64
    image_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    return image_png


if __name__ == '__main__':
    app.run(debug=True)
