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
            name = el['name']
            emp_name = el['employer']['name']
            date = el['published_at'][:10]
            url = el['alternate_url']
            result_list.append((name, emp_name, date, url))
    return result_list
