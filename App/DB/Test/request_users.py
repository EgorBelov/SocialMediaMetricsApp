import requests
import json
import tokens
from rdflib import Graph, Namespace, URIRef, Literal

def request_users():
    response = requests.get('https://api.vk.com/method/users.search', params={
            'access_token': tokens.access_user_token,
            'sort': 0,
            'count': 100,
            'v': '5.199',
            'fields': {'is_no_index', 'is_closed'},
        })

    users = json.loads(response.text)['response']['items']
    return users

# for user in search_vk_users():
#     if user['is_no_index'] == False: # возможность просматривать стену
#         print(user['first_name'])
