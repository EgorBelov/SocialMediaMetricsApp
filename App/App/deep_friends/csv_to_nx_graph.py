import networkx as nx
import psycopg2
import scipy
import operator




def write_to_csv(filename, fields, rows) -> None:
    '''
  Записать информацию в csv файл
  получает <- имя файла, поля (id, label и т.д.), строки (информация)
  возвращает -> None
  '''

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(fields + '\n')
        for row in rows:
            file.write(row + '\n')


def csv_to_networkx_dict(nodes_info, edges_info):
    # Создаем пустой граф
    G = nx.Graph()

    # Обрабатываем узлы
    nodes = nodes_info[1:]
    for node in nodes:
        node_data = node.strip().split(',')
        node_attributes = {field: value.strip('"') for field, value in zip(nodes_info[0].split(','), node_data)}
        G.add_node(node_attributes['id'], **node_attributes)

    # Обрабатываем ребра
    edges = edges_info[1:]
    for edge in edges:
        edge_data = edge.strip().split(',')
        source, target = edge_data[0].strip('"'), edge_data[1].strip('"')
        edge_attributes = {field: value.strip('"') for field, value in zip(edges_info[0].split(','), edge_data)}
        G.add_edge(source, target, **edge_attributes)

    return G


def calculate_graph_properties(G):
    res_metrics = []

    # Количество вершин
    num_nodes = G.number_of_nodes()
    print("Количество вершин:", num_nodes)

    # Количество ребер
    num_edges = G.number_of_edges()
    print("Количество ребер:", num_edges)

    # Связный граф
    is_connected = nx.is_connected(G)
    print("Связный граф:", is_connected)
    res_metrics.append(is_connected)

    # Диаметр графа
    diameter = nx.diameter(G)
    print("Диаметр графа:", diameter)

    res_metrics.append(diameter)
    res_metrics.append(diameter / 2)
    # # Центр графа
    # center = nx.center(G)
    # print("Центр графа:", center)

    # # Радиус графа
    # radius = nx.radius(G)
    # print("Радиус графа:", radius)

    # Page Rank

    print('Page Rank:', nx.pagerank(G)['16257176'])
    res_metrics.append(nx.pagerank(G)['16257176'])
    # Compute centrality metrics
    betweenness_centrality = nx.betweenness_centrality(G)
    degree_centrality = nx.degree_centrality(G)

    # Compute additional network metrics
    transitivity = nx.transitivity(G)
    assortativity = nx.degree_assortativity_coefficient(G)

    # Find the most influential user based on chosen metric (e.g., Betweenness Centrality)
    most_influential_user = max(betweenness_centrality, key=betweenness_centrality.get)
    # Print network metrics
    print(f"Most Influential User: {most_influential_user}")
    print(f"Betweenness Centrality: {betweenness_centrality[most_influential_user]}")
    print(f"Degree Centrality: {degree_centrality[most_influential_user]}")
    print(f"Transitivity: {transitivity}")
    print(f"Assortativity: {assortativity}")

    # Коэффициент кластеризации
    clustering_coefficient = nx.average_clustering(G)
    print("Коэффициент кластеризации:", clustering_coefficient)

    res_metrics.append(transitivity)
    res_metrics.append(assortativity)
    res_metrics.append(degree_centrality[most_influential_user])
    res_metrics.append(betweenness_centrality[most_influential_user])
    res_metrics.append(clustering_coefficient)
    return res_metrics


def main():
    nodes_file = 'nodes.csv'
    if not nodes_file.endswith('.csv'):
        nodes_file += '.csv'

    edges_file = 'edges.csv'
    if not edges_file.endswith('.csv'):
        edges_file += '.csv'

    with open(nodes_file, encoding='utf-8') as nodes_file:
        nodes_info = nodes_file.readlines()

    with open(edges_file, encoding='utf-8') as edges_file:
        edges_info = edges_file.readlines()

    graph_dict = csv_to_networkx_dict(nodes_info, edges_info)
    res = calculate_graph_properties(graph_dict)





    print(res)
    return res


if __name__ == '__main__':

    conn = psycopg2.connect(
        database="SocialMediaMetrics",
        user="postgres",
        password="123321",
        host="localhost",
        port="5432"
    )
    # Создание курсора
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vk_users')
    users_data = cursor.fetchall()
    for user in users_data:
        print(f'Количество вершин: {len(user[16])}. Запись в файл nodes.csv')
        write_to_csv('nodes.csv', 'id,label,type,sex,domain,country,city,bdate', user[16])

        print(f'Количество рёбер: {len(user[17])}. Запись в файл edges.csv')
        write_to_csv('edges.csv', 'source,target,weight', user[17])
        res = main()

        cursor.execute('''
               UPDATE vk_users
               SET сonnectivity = %s,
                   diameter = %s,
                   radius = %s,
                   page_rank = %s,
                   betweenness_centrality = %s,
                   degree_centrality = %s,
                   transitivity = %s,
                   assortativity = %s,
                   clustering_coefficient = %s
               WHERE id_vk = %s
           ''', (res[0], res[1], round(res[2], 0), round(res[3], 5), round(res[7], 5), round(res[6], 5), round(res[4], 5),
                 round(res[5], 5), user[1]))