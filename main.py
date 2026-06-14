# pip install python-dotenv
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('YANDEX_DISK_TOKEN')
#
if not TOKEN:
    raise RuntimeError('Яндекс-диск токен не установлен')

# ---------------------------------------------------------------------------------
class IpDetector:
    def get_ip(self):
        url_get_ip = 'https://api.ipify.org/?format=json'
        response = requests.get(url_get_ip)
        ip_address = response.json()['ip']
        return ip_address
    def get_geo_info(self):
            ip_address = self.get_ip()
            url_get_city=f'https://ipinfo.io/{ip_address}/geo'
            response = requests.get(url_get_city)
            city_name= response.json()['city']
            return {
                'ip': ip_address,
                'city': city_name
            }
# ---------------------------------------------------------------------------------
class YD:
    def __init__(self, token):
        self.token: str = token
        self.headers = {'Authorization': f'OAuth {self.token}'}
        self.base_url = 'https://cloud-api.yandex.net'

    def create_folder(self, path):
        response = requests.put(f'{self.base_url}/v1/disk/resources',
                                headers=self.headers,
                                params={'path': path})
        return response.status_code in [201, 409]

    def upload_file(self, local_file_path, path_disk):
        # Просим у Яндекса ссылку для загрузки
        response = requests.get(
            f'{self.base_url}/v1/disk/resources/upload',
            headers=self.headers,
            params={'path': path_disk,
                    'overwrite': 'true'
                    }
        )
        # Достаём ссылку загрузки
        uploaded_url = response.json()['href']

        # Открываем локальный файл
        with open(local_file_path, 'rb') as file:
            # Отправляем файл на специальную ссылку
            response = requests.put(uploaded_url,files={'file': file})
        #     Проверяем успешность
        return 200 <= response.status_code < 300

    def delete_folder(self, path):
        pass

# ---------------------------------------------------------------------------------

def save_json(data,filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return filename
# ---------------------------------------------------------------------------------
def main():
    ip_detector = IpDetector()
    geo_info = ip_detector.get_geo_info()

    local_file_path=save_json(geo_info, 'geo_info.json')

    yd = YD(TOKEN)

    yd.create_folder('IpDetectorFiles')

    uploaded = yd.upload_file(
        local_file_path,
        'IpDetectorFiles/geo_info.json'
    )
    if uploaded:
        print('Файл успешно загружен')

    os.remove(local_file_path)

if __name__ == '__main__':
    main()

