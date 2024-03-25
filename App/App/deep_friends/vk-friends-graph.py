import psycopg2
import requests
import os
import time

from tokens import access_user_token, access_user_token_1
from csv_to_nx_graph import csv_to_networkx_dict, calculate_graph_properties, main


def get_user_info(user_id, fields, token, api_version) -> dict:
    '''
  Получить информацию о человеке по его user_id
  получает <- ID человека, поля (имя, город и т.д.), токен, версию API
  возвращает -> API ответ (JSON) в формате словаря
  '''

    params = {'user_id': int(user_id),
              'fields': ','.join(fields),
              'name_case': 'Nom',
              'v': api_version,
              'access_token': token}
    url = 'https://api.vk.com/method/users.get'

    try:
        req = requests.get(url, params=params)
        user = req.json()['response'][0]
    except:
        raise ValueError('Wrong user id or server error')

    return user


def make_dict_from_user_info(user, user_type) -> dict:
    '''
  Обработать API ответ от сервера для удобного отображения
  получает <- словарь (API ответ), тип пользователя (я, друг, друг друга)
  возвращает ->  обработанный словарь с информацией о человеке
  '''

    user_info = {}

    # Обязательные поля
    user_info['id'] = str(user['id'])
    user_info['name'] = (user['first_name'] + ' ' + user['last_name']).strip()
    user_info['type'] = str(user_type)
    user_info['gender'] = 'male' if user['sex'] == 2 else 'female'
    user_info['domain'] = 'vk.com/' + user['domain']

    # Необязательные поля
    user_info['country'] = user['country']['title'] if user.get('country') else 'Unknown'
    user_info['city'] = user['city']['title'] if user.get('city') else 'Unknown'
    user_info['bdate'] = user['bdate'] if user.get('bdate') else 'Unknown'

    return user_info


def make_node_from_user_info(user_info) -> str:
    # Преобразовать словарь с информацией о человеке в вершину графа

    new_node = []
    for key in user_info:
        new_node.append(user_info[key])
    new_node = ','.join(new_node)

    return new_node


def write_to_csv(filename, fields, rows) -> None:
    '''
    Записать информацию в csv файл
    получает <- имя файла, поля (id, label и т.д.), строки (информация)
    возвращает -> None
    '''

    # Открываем файл в режиме записи и обрезаем его до нулевой длины
    with open(filename, 'w', encoding='utf-8') as file:
        file.truncate(0)
        # Записываем заголовок
        file.write(fields + '\n')
        # Записываем строки
        for row in rows:
            file.write(row + '\n')


def request_friends(user_id, count, fields, token, api_version) -> dict:
    '''
  Получить список друзей человека по его user_id
  получает <- ID человека, количество друзей, поля (имя, город и т.д.), токен, версию API
  возвращает -> API ответ (JSON) в формате словаря
  '''

    url = f'https://api.vk.com/method/friends.get'
    params = {'v': api_version,
              'access_token': token,
              'user_id': user_id,
              'count': count,
              'fields': ','.join(fields)}
    return requests.get(url, params=params).json()['response']


def is_mutual(friend, my_friends) -> bool:
    '''
  Проверить, есть ли человек в списке друзей
  получает <- человека для проверки, список друзей
  возвращает -> True, если человек есть в списке друзей, False если нет
  '''

    for person in my_friends:
        if person['id'] == friend['id']:
            return True
    return False


# Инициализация токена
token = os.environ.get('TOKEN')
if not token:
    # print('Токен не найден в переменных окружения')
    # token = input('Введите токен: ')
    token = access_user_token_1
# Версия API и запрашиваемые поля
version = '5.199'
fields = ['sex', 'bdate', 'city', 'country', 'domain']


def create_graph(user_uid):

    # Инициализация человека для которого будет строиться граф
    while True:
        # user_id = input('Введите цифровой ID: ')
        user_id = str(user_uid)
        print('Получение информации об аккаунте')

        try:
            # Получить информацию о человеке по ID
            user = get_user_info(user_id, fields, token, version)
            user = make_dict_from_user_info(user, 'me')
            break
        except ValueError:
            print('Не удалось получить информацию')
            continue

    print('Имя:', user.get('name'))

    while True:
        try:
            # print('Введите максимальное количество друзей для одного человека')
            # print('(рекомендуется 100-250)')
            # count = int(input('Ваш выбор: '))
            count = 250
            break
        except:
            print('Ошибка ввода, повторите.')

    # Запрос списка друзей
    print('Получение списка друзей')
    my_friends = request_friends(user_id, count, fields, token, version)['items']
    print('Количество друзей:', len(my_friends))

    # drop_without_mutuals = True if \
    #   input('Пропускать людей без общих с человеком друзей? (y/n): ').lower() == 'y' else False
    drop_without_mutuals = False

    dropped = 0

    # Инициализация списков вершин и рёбер
    edges, nodes = [], []
    # Добавить первого человека в граф
    nodes.append(make_node_from_user_info(user))

    # Инициализация списка друзей друзей
    friends_of_friends = []
    open_accounts = 0

    # Для каждого друга получить список его друзей
    for i, friend in enumerate(my_friends):
        print(f'Получение списка друзей друзей: {i + 1}/{len(my_friends)}', end='\r')

        mutual_friends = 1
        try:
            # Запрос в API
            request = request_friends(friend.get('id'), count, fields, token, version)['items']
        except:
            continue

        # Если успешно, аккаунт не закрыт
        open_accounts += 1

        # Подсчет общих друзей
        for _friend in request:
            if is_mutual(_friend, my_friends):
                mutual_friends += 1

        # Пропустить человека, если нет общих друзей и drop_without_mutuals=True
        if drop_without_mutuals and mutual_friends < 2:
            dropped += 1
            time.sleep(0.5)
            continue

        # Добавить ребра от друга до каждого его друга
        for _friend in request:
            friends_of_friends.append(_friend)
            edges.append(f"{friend['id']},{_friend['id']},1")

        # Добавить ребро до друга
        edges.append(f"{user_id},{friend['id']},{mutual_friends}")

        # Добавить друга в списко вершин
        friend = make_dict_from_user_info(friend, 'friend')
        nodes.append(make_node_from_user_info(friend))

        time.sleep(0.5)

    print('\nЗакрытых аккаунтов среди друзей:', len(my_friends) - open_accounts)
    if drop_without_mutuals:
        print('Пропущено друзей:', dropped)

    # Добавить вершины для друзей друзей
    for friend in friends_of_friends:
        friend = make_dict_from_user_info(friend, 'friend_of_friend')
        new_node = make_node_from_user_info(friend)

        if new_node not in nodes:
            nodes.append(new_node)

    print(f'Количество вершин: {len(nodes)}. Запись в файл nodes.csv')
    write_to_csv('nodes.csv', 'id,label,type,sex,domain,country,city,bdate', nodes)

    print(f'Количество рёбер: {len(edges)}. Запись в файл edges.csv')
    write_to_csv('edges.csv', 'source,target,weight', edges)

    print('Готово!')

if __name__ == '__main__':
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

    for user in users_data:
        create_graph(user[1])
        # Засекаем время начала выполнения функции
        start_time = time.time()
        res = main()
        # Засекаем время окончания выполнения функции
        end_time = time.time()

        # Вычисляем время выполнения функции в секундах
        execution_time_seconds = end_time - start_time

        # Преобразуем время выполнения из секунд в минуты
        execution_time_minutes = execution_time_seconds / 60

        print("Время выполнения функции:", execution_time_minutes, "минут")

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
                         round(res[5], 5), round(res[8], 5), user[1]))


    # Сохранение изменений и закрытие соединения
    conn.commit()
    cursor.close()
    conn.close()