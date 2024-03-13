import requests
import json
import tokens


def request_groups():
    response = requests.get('https://api.vk.com/method/groups.search', params={
            'access_token': tokens.access_user_token,
            'q': 'и',
            'count': 40,
            'v': '5.199',

        })

    groups = json.loads(response.text)['response']['items']
    return groups