import requests
import json

with open("regioni.json", "r") as f:
    AREAS = json.load(f)

URL = 'https://api.hh.ru/vacancies'


def get_vac(search, area):
    par = {'text': search, 'area': AREAS[area.lower()], 'per_page': '10'}
    req = requests.get(URL, params=par)
    raw_data = req.json()['items']
    result_list = []
    for el in raw_data:
        if el['type']['id'] == 'open':
            id = el['id']
            name = el['name']
            emp_name = el['employer']['name']
            date = el['published_at'][:10]
            url = el['alternate_url']
            if not el['salary']:
                salary = 'не указана'
            else:
                if not el["salary"]['currency']:
                    if not el["salary"]["to"]:
                        salary = f'{el["salary"]["from"]} RUR'
                    else:
                        salary = f'от {el["salary"]["from"]} до {el["salary"]["to"]} RUR'
                else:
                    if not el["salary"]["to"]:
                        salary = f'{el["salary"]["from"]} {el["salary"]["currency"]}'
                    else:
                        salary = f'от {el["salary"]["from"]} до {el["salary"]["to"]} {el["salary"]["currency"]}'
            result_list.append((id, name, emp_name, date, url, salary))
    return result_list
