import requests
import json
from App.DB.requests import tokens


def request_count_likes_from_wall(id):
        response = requests.get('https://api.vk.com/method/wall.get', params={
                'access_token': tokens.access_user_token_1,
                'owner_id': id,
                'v': '5.199',
                'filter': 'all',
                'count': 10,
            })

        # Получаем информацию
        wall_info = json.loads(response.text)['response']['items']

        likes_count = sum([post['likes']['count'] for post in wall_info])
        reposts_count = sum([post['reposts']['count'] for post in wall_info])
        comments_count = sum([post['comments']['count'] for post in wall_info])
        #print(id)
        return [likes_count, reposts_count, comments_count, len(wall_info)]

# print(f'количество лайков: {likes_count}')
# print(f'количество репостов: {reposts_count}')
# print(f'количество комментов: {comments_count}')
#(request_count_likes_from_wall(673687878))