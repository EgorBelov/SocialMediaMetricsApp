import requests
import json

from App.DB.requests_api_VK import tokens


def request_users_get(user_ids):
    str_uids = ', '.join(user_ids)

    response = requests.get('https://api.vk.com/method/users.get', params={
            'access_token': tokens.access_user_token_1,
            'user_ids': str_uids,
            'v': '5.199',
            'fields': 'is_no_index, is_closed',
        })

    users = json.loads(response.text)['response']
    return users