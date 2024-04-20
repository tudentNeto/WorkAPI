import requests


class YaApiClient():
    URL_BASE = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token = token

    def get_common_headers(self):
        return {'Authorization': 'OAuth ' + self.token}

    def get_ref_source(self, path):
        params = {'path': path}
        return requests.put(self.URL_BASE, headers=self.get_common_headers(), params=params)


    def is_exist_source(self, path):
        params = {'path': path}
        return True if (requests.get(self.URL_BASE, headers=self.get_common_headers(), params=params).status_code == 200) else False
    def ref_for_save(self, source_and_name_file):
        response = requests.get(self.URL_BASE + '/upload',
                                headers=self.get_common_headers(),
                                params={'path': source_and_name_file})
        return response.json().get('href', '')
