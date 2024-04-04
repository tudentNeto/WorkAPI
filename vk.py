import configparser
import datetime
import json
import logging
import requests
import time


class VKApiClient():
    API_BASE_URL='https://api.vk.com/method/'

    def __init__(self, access_token, user_id):
        self.token = access_token
        self.user_id=user_id
        

    def get_common_params(self):
        return {'access_token': self.token, 'owner_id': self.user_id, 'v': '5.131'}


    def get_user_photo(self, album_id='wall'):
        params = self.get_common_params()
        params['album_id']=album_id
        params['extended']=1
        response=requests.get('https://api.vk.com/method/photos.get', params=params)
        return response
    

class YaApiClient():
    URL_BASE='https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token=token
        

    def get_common_headers(self):
        return {'Authorization': 'OAuth ' + self.token}
    
    
    def get_ref_source(self, path):
        params={'path': path}
        return requests.put(self.URL_BASE, headers=self.get_common_headers(), params=params)
    
    
    def ref_for_save(self, source_and_name_file):
        response=requests.get(self.URL_BASE + '/upload',
                              headers=self.get_common_headers(),
                              params={'path': source_and_name_file})
        return response.json().get('href','')
        

config=configparser.ConfigParser()
config.read('config.ini')
user_id=config.get('Settings', 'id')
access_token=config.get('Settings', 'access_token')
token=config.get('Settings', 'token')

logging.basicConfig(filename='vkLog.txt', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug('--Начало программы')

vk=VKApiClient(access_token, user_id)
ya=YaApiClient(token)

fl_err=False
list_res=[]
name_source='ImageVK'
if 200<=ya.get_ref_source(name_source).status_code<300:
    logging.debug('--Создана папка ' + name_source + ' на Яндекс.Диск')
    L=[]

    for i in range(5):
        print('Обрабатывается фото № ' + str(i+1) + ' . . .')
        dict_curr={}
        name_f_part=[]
        logging.debug('--[' + str(i+1) + '] итерация')
        dict_answer=vk.get_user_photo().json()
        if dict_answer.get('response',0)!=0:

            max_=1
            type_size=''
            url_file=''
            for el in dict_answer['response']['items'][i]['sizes']:
                multiple=int(el['width'])*int(el['height'])
                if multiple>max_:
                    max_=multiple
                    type_size=el['type']
                    url_file=el['url']
        
            dict_curr['size']=type_size
            logging.debug('--Получен url фото ' + str(i+1))
            url_file=dict_answer['response']['items'][i]['sizes'][-1]['url']
            likes_part=dict_answer['response']['items'][i]['likes']['count']
            name_f_part.append(str(likes_part))
            dts=dict_answer['response']['items'][i]['date']
            date_part=datetime.datetime.fromtimestamp(dts).date()
            name_f_part.append(date_part.isoformat())
            name_f_part.append(str(i))
            name_file=""
            for j in range(3):
                name_file+=name_f_part[j]
                if name_file not in L:
                    break
                name_file+='_'
            L.append(name_file)
            name_file=name_file + '.jpg'
            logging.debug('--Фото ' + str(i+1) + ' будет сохранено с именем: ' + name_file)
            dict_curr['file_name']=name_file
            url_for_save=ya.ref_for_save(name_source + '/' + name_file)
            if url_for_save:
                if 200<=requests.put(url_for_save, files={'file': requests.get(url_file).content}).status_code <300:
                    logging.debug('--Фото ' + str(i+1) + ' успешно сохранено!')
                    list_res.append(dict_curr)
                    print('Фото № ' + str(i+1) + ' сохранено с именем ' + name_file)
                else:
                    logging.debug('--Ошибка Ya! Фото не сохранено')
                    fl_err=True
            else:
                print('Ошибка!')
                logging.debug('--Ошибка Ya (нет ссылки)')
                fl_err=True
        else:
            logging.debug('--Ошибка VK! Код:' + str(dict_answer['error']['error_code']) + ' Сообщение: ' + dict_answer['error']['error_msg'])
            fl_err=True

else:
    logging.debug('--Ошибка Yandex! Папка ' + name_source + ' не создана!')
    fl_err=True
with open('vkJson.json', 'w') as f:
    json.dump(list_res,f,indent=4)
logging.debug('--Информация о файлах ' + ('ОТСУТСТВУЕТ!!!' if fl_err else 'сохранена (см. файл vkJson)'))
logging.debug('--Конец!')
print('Работа программы завершилась ' + ('с ошибкой!' if fl_err else 'успешно!'))
