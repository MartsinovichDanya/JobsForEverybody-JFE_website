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
                    elif not el["salary"]["from"]:
                        salary = f'{el["salary"]["to"]} RUR'
                    else:
                        salary = f'от {el["salary"]["from"]} до {el["salary"]["to"]} RUR'
                else:
                    if not el["salary"]["to"]:
                        salary = f'{el["salary"]["from"]} {el["salary"]["currency"]}'
                    elif not el["salary"]["from"]:
                        salary = f'{el["salary"]["to"]} {el["salary"]["currency"]}'
                    else:
                        salary = f'от {el["salary"]["from"]} до {el["salary"]["to"]} {el["salary"]["currency"]}'
            result_list.append((id, name, emp_name, date, url, salary))
    return result_list


def count_sred_zp(search, area):
    pages = []
    all_zp = 0
    all_n = 0

    for i in range(5):
        url = 'https://api.hh.ru/vacancies'
        par = {'text': search, 'area': AREAS[area.lower()], 'per_page': '100', 'page': i}
        req = requests.get(url, params=par)
        res = req.json()
        pages.append(res)
    for page in pages:
        try:
            vacancies = page['items']
            n = 0
            sum_zp = 0
            for vacancy in vacancies:
                if vacancy['salary'] is not None:
                    sal = vacancy['salary']
                    if sal['from'] is not None:
                        n += 1
                        sum_zp +=sal['from']
            all_zp += sum_zp
            all_n += n
        except Exception:
            pass
    av_zp = all_zp / all_n
    return int(av_zp)
