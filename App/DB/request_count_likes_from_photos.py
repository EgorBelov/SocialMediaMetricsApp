import requests
import json
import tokens

def request_count_likes_from_photos(id):
    response = requests.get('https://api.vk.com/method/photos.get', params={
            'access_token': tokens.access_user_token,
            'owner_id': str(id),
            'v': '5.199',
            'extended': True,
            'album_id': 'profile'
        })

    photos = json.loads(response.text)['response']['items']

    counts = json.loads(response.text)['response']['count']
    total_likes = sum([photo['likes']['count'] for photo in photos])
    avg_likes = total_likes / counts if counts != 0 else 0  # избегаем деления на ноль
    #print(id)

    return format(avg_likes, '.3f')


#print(request_count_likes_from_photos(406989548))