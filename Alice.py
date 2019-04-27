from flask import Flask, request
import logging
import json


from DB import DB
from Models import AliceUserModel, VacModel
from API_kicker import get_vac
from emailer import send_email

app = Flask(__name__)
db = DB('alice_jfe.db')

logging.basicConfig(level=logging.INFO)


def email_validate(email):
    if '@' in email and '.' in email:
        return True
    return False


with open("regioni.json", "r") as f:
    VALID_AREAS = json.load(f).keys()


def validate_area(area):
    if area not in VALID_AREAS:
        return False
    return True


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


settings_flags = {'set_search': False, 'set_area': False, 'set_email': False}
cur_vac = 0


def handle_dialog(res, req):
    global cur_vac
    user_id = req['session']['user_id']
    aum = AliceUserModel(db.get_connection())
    vm = VacModel(db.get_connection())
    vac_count = vm.get_count(user_id) - 1
    if not aum.exists(user_id)[0]:
        res['response']['text'] = '''Привет! Я - Алиса.
                                     Я могу помочь найти тебе работу.
                                     Назови своё имя!'''
        aum.insert(user_id, None, None, None, None)
        return

    if not aum.get(user_id)[1]:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            aum.update_name(user_id, first_name)
            res['response']['text'] = f'''Приятно познакомиться, {first_name.title()}.
                                    Прежде, чем мы начнем, {first_name.title()}, мне нужна кое-какая информация о тебе
                                    Пожалуйста введи свою почту, слова для поиска вакансий и город,
                                    в котором ты хочешь найти работу, именно в таком порядке.
                                    (Пример правильного сообщения - example@example.com, бугалтер, санкт-петербург)'''

    elif not aum.get(user_id)[2]:
        data = [el.strip().lower() for el in req['request']['original_utterance'].split(',')]
        if len(data) < 3 or not email_validate(data[0]) or not validate_area(data[2]):
            res['response']['text'] = '''Данные введены неправильно.
                                    (Пример правильного сообщения - example@example.com, бухгалтер, санкт-петербург)'''
        else:
            aum.update_email(user_id, data[0])
            aum.update_search_words(user_id, data[1])
            aum.update_area(user_id, data[2])
            res['response']['text'] = f'''Поздравляю, {aum.get(user_id)[1].capitalize()}, все готово!
                                          Поищем что-нибудь?
                                          (чтобы поменять настройки напиши - настройки)'''
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'настройки',
                    'hide': True
                }
            ]

    else:
        if req['request']['original_utterance'] == 'настройки':
            res['response']['text'] = 'Выбери один из вариантов'
            res['response']['buttons'] = [
                {
                    'title': 'Настроить поиск',
                    'hide': True
                },
                {
                    'title': 'Настроить город',
                    'hide': True
                },
                {
                    'title': 'Настроить почту',
                    'hide': True
                }
            ]

        if settings_flags['set_search']:
            aum.update_search_words(user_id, req['request']['original_utterance'])
            res['response']['text'] = '''Поиск настроен!
                                        Поищем что-нибудь?'''
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'настройки',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
            settings_flags['set_search'] = False

        if settings_flags['set_email']:
            email = req['request']['original_utterance']
            if email_validate(email):
                res['response']['text'] = '''Почта настроена!
                                            Поищем что-нибудь?'''
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'настройки',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
                aum.update_email(user_id, email)
                settings_flags['set_email'] = False
            else:
                res['response']['text'] = 'Некорректный адрес почты! Попробуй еще раз.'

        if settings_flags['set_area']:
            area = req['request']['original_utterance'].lower()
            if validate_area(area):
                res['response']['text'] = '''Город настроен!
                                            Поищем что-нибудь?'''
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'настройки',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
                aum.update_area(user_id, area)
                settings_flags['set_area'] = False
            else:
                res['response']['text'] = 'Такого города нет.'

        if req['request']['original_utterance'] == 'Настроить поиск':
            res['response']['text'] = 'введи ключевые слова для поиска'
            settings_flags['set_search'] = True
            res['response']['buttons'] = []

        elif req['request']['original_utterance'] == 'Настроить почту':
            res['response']['text'] = 'введи почту'
            settings_flags['set_email'] = True
            res['response']['buttons'] = []

        elif req['request']['original_utterance'] == 'Настроить город':
            res['response']['text'] = 'введи город'
            settings_flags['set_area'] = True
            res['response']['buttons'] = []

        if req['request']['original_utterance'] == '':
            name = aum.get(user_id)[1]
            res['response']['text'] = f'''Привет, {name.capitalize()}.
                                                  Поищем что-нибудь?
                                                  (чтобы поменять настройки напиши - настройки)'''
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'настройки',
                    'hide': True
                }
            ]

    if 'нет' in req['request']['nlu']['tokens'] or 'завершить' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Ну ладно.'
        res['response']['end_session'] = True

    if 'да' in req['request']['nlu']['tokens']:
        data = aum.get(user_id)
        search = data[3]
        area = data[4]
        vac_list = get_vac(search, area)
        for el in vac_list:
            vm.insert(*el, user_id=user_id)
        if len(vac_list) == 0:
            res['response']['text'] = 'К сожалению, ничего не найдено.'
            res['response']['buttons'] = [
                {
                    'title': 'настройки',
                    'hide': True
                },
                {
                    'title': 'завершить',
                    'hide': True
                }
            ]
        else:
            vac_data = vac_list[cur_vac]
            res['response']['text'] = f'''{vac_data[1]}
                                        Работодатель - {vac_data[2]}
                                        Дата публикации - {vac_data[3]}
                                        Зарплата - {vac_data[5]}'''
            res['response']['buttons'] = [
                {
                    'title': 'ещё',
                    'hide': True
                },
                {
                    'title': 'перейти на hh.ru',
                    'hide': True,
                    'url': vac_data[4]
                },
                {
                    'title': 'завершить',
                    'hide': True
                }
            ]
    if 'ещё' in req['request']['nlu']['tokens']:
        vac_list = vm.get_all(user_id)
        cur_vac += 1
        if cur_vac > vac_count:
            res['response']['text'] = 'Это пока все. Ты можешь изменить настройки и поискать еще'
            res['response']['buttons'] = [
                {
                    'title': 'настройки',
                    'hide': True
                },
                {
                    'title': 'отправь на почту',
                    'hide': True
                },
                {
                    'title': 'отчистить список вакансий',
                    'hide': True
                },
                {
                    'title': 'завершить',
                    'hide': True
                }
            ]
            cur_vac = 0
        else:
            vac_data = vac_list[cur_vac]
            res['response']['text'] = f'''{vac_data[2]}
                                        Работодатель - {vac_data[3]}
                                        Дата публикации - {vac_data[4]}
                                        Зарплата - {vac_data[6]}'''
            res['response']['buttons'] = [
                {
                    'title': 'ещё',
                    'hide': True
                },
                {
                    'title': 'перейти на hh.ru',
                    'hide': True,
                    'url': vac_data[5]
                },
                {
                    'title': 'завершить',
                    'hide': True
                }
            ]
    if req['request']['original_utterance'] == 'перейти на hh.ru':
        res['response']['text'] = 'ок'
        res['response']['buttons'] = [
            {
                'title': 'ещё',
                'hide': True
            },
            {
                'title': 'завершить',
                'hide': True
            }
        ]

    if req['request']['original_utterance'] == 'отправь на почту':
        res['response']['text'] = 'отправлено'
        res['response']['buttons'] = [
            {
                'title': 'настройки',
                'hide': True
            },
            {
                'title': 'завершить',
                'hide': True
            }
        ]
        vacancies = vm.get_all(user_id)
        text = '\n'.join([f'{el[2]} - {el[5]}' for el in vacancies])
        send_email(aum.get(user_id)[2], text)

    if req['request']['original_utterance'] == 'отчистить список вакансий':
        res['response']['text'] = 'ок'
        res['response']['buttons'] = [
            {
                'title': 'настройки',
                'hide': True
            },
            {
                'title': 'завершить',
                'hide': True
            }
        ]
        vm.delete_for_user(user_id)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
