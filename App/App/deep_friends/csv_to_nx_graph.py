import networkx as nx
import scipy
import operator

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
    # Количество вершин
    num_nodes = G.number_of_nodes()
    print("Количество вершин:", num_nodes)

    # Количество ребер
    num_edges = G.number_of_edges()
    print("Количество ребер:", num_edges)

    # Связный граф
    # is_connected = nx.is_connected(G)
    # print("Связный граф:", is_connected)
    #
    # # Диаметр графа
    # diameter = nx.diameter(G)
    # print("Диаметр графа:", diameter)
    #
    # # Центр графа
    # center = nx.center(G)
    # print("Центр графа:", center)
    #
    # # Радиус графа
    # radius = nx.radius(G)
    # print("Радиус графа:", radius)

    # Page Rank

    print('Page Rank:', nx.pagerank(G)['16257176'])
    # Compute centrality metrics
    # betweenness_centrality = nx.betweenness_centrality(G)
    # degree_centrality = nx.degree_centrality(G)
    #
    # # Compute additional network metrics
    # transitivity = nx.transitivity(G)
    # assortativity = nx.degree_assortativity_coefficient(G)
    #
    # # Find the most influential user based on chosen metric (e.g., Betweenness Centrality)
    # most_influential_user = max(betweenness_centrality, key=betweenness_centrality.get)
    # # Print network metrics
    # print(f"Most Influential User: {most_influential_user}")
    # print(f"Betweenness Centrality: {betweenness_centrality[most_influential_user]}")
    # print(f"Degree Centrality: {degree_centrality[most_influential_user]}")
    # print(f"Transitivity: {transitivity}")
    # print(f"Assortativity: {assortativity}")

    # Коэффициент кластеризации
    clustering_coefficient = nx.average_clustering(G)
    print("Коэффициент кластеризации:", clustering_coefficient)

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
    calculate_graph_properties(graph_dict)
    # Теперь вы можете использовать graph_dict для создания графа с помощью NetworkX
    # Пример: nx_graph = nx.Graph(graph_dict)

if __name__ == '__main__':
    main()
