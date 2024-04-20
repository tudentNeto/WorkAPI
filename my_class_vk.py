import requests


class VKApiClient():
    API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token, user_id):
        self.token = access_token
        self.user_id = user_id

    def get_common_params(self):
        return {'access_token': self.token, 'owner_id': self.user_id, 'v': '5.131'}

    def get_user_photo(self, album_id='wall'):
        params = self.get_common_params()
        params['album_id'] = album_id
        params['extended'] = 1
        response = requests.get('https://api.vk.com/method/photos.get', params=params)
        return response


