import requests
import tokens


def request_counts_friends_followers(id):
    response = requests.get('https://api.vk.com/method/users.get', params={
        'access_token': tokens.access_token,
        'user_ids': str(id),
        'v': '5.199',
        'fields': 'counters'
    })

    response.raise_for_status()  # Check if the request was successful

    user_data = response.json().get('response')[0]
    counters = user_data.get('counters', {})

    followers_count = counters.get('followers', 0)

    response = requests.get('https://api.vk.com/method/friends.get', params={
        'access_token': tokens.access_token,
        'user_id': str(id),
        'v': '5.199',
        'count': 1,

    })

    response.raise_for_status()  # Check if the request was successful

    user_data = response.json().get('response')

    friends_count = user_data.get('count', 0)

    return [followers_count, friends_count]

# print(request_counts_friends_followers(673687878))
