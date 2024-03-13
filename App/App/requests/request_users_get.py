import requests
import json

from App.requests import tokens


def request_users_get(user_ids):
    response = requests.get('https://api.vk.com/method/users.get', params={
            'access_token': tokens.access_user_token,
            'user_ids': user_ids,
            'v': '5.199',
            'fields': 'is_no_index, is_closed',
        })

    users = json.loads(response.text)['response']
    return users