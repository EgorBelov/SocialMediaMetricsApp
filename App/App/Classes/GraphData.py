import base64
import io

import plotly.graph_objects as go
from matplotlib import pyplot as plt


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


pagerank_data = [10, 20, 30, 40, 50]  # Пример данных метрик
user_names = ['Иван Иванов', 'Петр Петров', 'Алексей Сидоров', 'Мария Иванова', 'Ольга Петрова']  # Пример имен и фамилий пользователей
pagerank_graph = create_graph(user_names, pagerank_data, 'PageRank Graph')  # Создание графика PageRank
