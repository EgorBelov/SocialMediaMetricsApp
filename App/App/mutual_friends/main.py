import json
import sys
import time
import operator
import networkx as nx
import requests
from .settings import token, my_id, api_v, max_workers, delay, deep


def force(f, delay=delay):
    """При неудачном запросе сделать паузу и попробовать снова"""

    def tmp(*args, **kwargs):
        while True:
            try:
                res = f(*args, **kwargs)
                break
            except KeyError:
                time.sleep(delay)
        return res

    return tmp


class VkException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class VkFriends():
    """
	Находит друзей, находит общих друзей
	"""
    parts = lambda lst, n=25: (lst[i:i + n] for i in iter(range(0, len(lst), n)))
    make_targets = lambda lst: ",".join(str(id) for id in lst)

    def __init__(self, *pargs):
        try:
            self.token, self.my_id, self.api_v, self.max_workers = pargs
            self.my_name, self.my_last_name, self.photo = self.base_info([self.my_id])
            self.all_friends, self.count_friends = self.friends(self.my_id)
        except VkException as error:
            sys.exit(error)

    def request_url(self, method_name, parameters, access_token=True):
        """read https://vk.com/dev/api_requests"""

        req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}'.format(
            method_name=method_name, api_v=self.api_v, parameters=parameters)

        if access_token:
            req_url = '{}&access_token={token}'.format(req_url, token=self.token[0])

        return req_url

    def base_info(self, ids):
        """read https://vk.com/dev/users.get"""
        r = requests.get(self.request_url('users.get', 'user_ids=%s&fields=photo' % (','.join(map(str, ids))))).json()
        if 'error' in r.keys():
            raise VkException('Error message: %s Error code: %s' % (r['error']['error_msg'], r['error']['error_code']))
        r = r['response'][0]
        # Проверяем, если id из settings.py не деактивирован
        if 'deactivated' in r.keys():
            raise VkException("User deactivated")
        return r['first_name'], r['last_name'], r['photo']

    def friends(self, id):
        """
        read https://vk.com/dev/friends.get
        Принимает идентификатор пользователя
        """
        # TODO: слишком много полей для всего сразу, город и страна не нужны для нахождения общих друзей
        response = requests.get(self.request_url('friends.get',
                                                 'user_id=%s&fields=uid,first_name,last_name,photo' % id)).json()[
            'response']

        # Фильтрация по условию, пропускаем записи с полем "deactivated"
        filtered_items = [item for item in response.get('items', []) if 'deactivated' not in item]

        return {item['id']: item for item in filtered_items}, response['count']

    def common_friends(self):
        """
        read https://vk.com/dev/friends.getMutual and read https://vk.com/dev/execute
        Возвращает в словаре кортежи с инфой о цели и списком общих друзей с инфой
        """
        result = []

        def get_mutual_friends(source, targets):
            vk_friends_list = VkFriends.make_targets(targets)

            try:
                r = requests.get(self.request_url('friends.getMutual',
                                                  f'source_uid={source}&target_uids={vk_friends_list}',
                                                  access_token=True)).json()['response']
                return r
            except Exception as e:
                print(f"Error getting mutual friends: {e}")
                return None

        # разбиваем список на части - по 25 в каждой
        for i in VkFriends.parts(list(self.all_friends.keys())):
            mutual_friends_response = get_mutual_friends(self.my_id, i)

            if mutual_friends_response:
                for x, id in enumerate(i):
                    target_id = int(id)

                    if 'error' in mutual_friends_response[x]:
                        error_code = mutual_friends_response[x]['error']['error_code']
                        if error_code == 18:  # User is deleted or banned
                            print(f"Skipping user {target_id} as they are deleted or banned.")
                            continue

                    common_friends = mutual_friends_response[x]
                    if isinstance(common_friends['common_friends'], list):
                        common_friends_info = [self.all_friends.get(int(friend_id)) for friend_id in common_friends['common_friends']]
                        result.append((self.all_friends[target_id], common_friends_info))
                    else:
                        print(f"Invalid common_friends response for user {target_id}: {common_friends}")

        return result




if __name__ == '__main__':
    a = VkFriends(token, my_id, api_v, max_workers)
    #print(a.my_name, a.my_last_name, a.my_id, a.photo)
    #df = a.common_friends()


    #print(df)

