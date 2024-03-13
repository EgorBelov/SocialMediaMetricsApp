import requests
import json
import tokens
from rdflib import Graph, Namespace, URIRef, Literal

def request_users_get(user_ids):
    response = requests.get('https://api.vk.com/method/users.get', params={
            'access_token': tokens.access_user_token,
            'user_ids': user_ids,
            'v': '5.199',
            'fields': 'is_no_index, is_closed',
        })

    users = json.loads(response.text)['response']
    return users


user = request_users_get('16257176, 1812605, 84006516, 475885221,181507171,557450182, 131850969,486363517,181273806')
print('sgdgs')