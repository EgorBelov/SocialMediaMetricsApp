import requests
import json

from App.DB.requests import tokens


def request_count_followers(id):

    response = requests.get('https://api.vk.com/method/users.getFollowers', params={
            'access_token': tokens.access_user_token_1,
            'user_id': id,
            'v': '5.199',
        })

    count = json.loads(response.text)['response']['count']
    return count