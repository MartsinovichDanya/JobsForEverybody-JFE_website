from flask import Flask, request
import logging
import json
import random


from DB import DB
from Models import AliceUserModel, VacModel

app = Flask(__name__)
db = DB('alice_jfe.db')

logging.basicConfig(level=logging.INFO)


def email_validate(email):
    if '@' in email and '.' in email:
        return True
    return False


with open("regioni.json", "r") as f:
    AREAS = json.load(f)
    VALID_AREAS = AREAS.keys()


def find_area_code(area):
    if area not in VALID_AREAS:
        return False
    return AREAS[area]


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


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    aum = AliceUserModel(db.get_connection())
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
        if len(data) < 3 or not email_validate(data[0]) or not find_area_code(data[2]):
            res['response']['text'] = '''Данные введены неправильно.
                                    (Пример правильного сообщения - example@example.com, бугалтер, санкт-петербург)'''
        else:
            aum.update_email(user_id, data[0])
            aum.update_search_words(user_id, data[1])
            aum.update_area(user_id, find_area_code(data[2]))
            print(aum.get(user_id))
            res['response']['text'] = f'''Поздравляю, {aum.get(user_id)[1].capitalize()}, все готово!
                                          Поищем что-нибудь?'''

    else:
        name = aum.get(user_id)[1]
        res['response']['text'] = f'''Привет, {name}.
                                      Поищем что-нибудь?'''
        res['response']['buttons'] = [
            {
                'title': 'Да',
                'hide': True
            },
            {
                'title': 'Нет',
                'hide': True
            }
        ]

#     else:
#         # У нас уже есть имя, и теперь мы ожидаем ответ на предложение сыграть.
#         # В sessionStorage[user_id]['game_started'] хранится True или False в зависимости от того,
#         # начал пользователь игру или нет.
#         if not sessionStorage[user_id]['game_started']:
#             # игра не начата, значит мы ожидаем ответ на предложение сыграть.
#             if 'да' in req['request']['nlu']['tokens']:
#                 # если пользователь согласен, то проверяем не отгадал ли он уже все города.
#                 # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
#                 if len(sessionStorage[user_id]['guessed_cities']) == 3:
#                     # если все три города отгаданы, то заканчиваем игру
#                     res['response']['text'] = 'Ты отгадал все города!'
#                     res['end_session'] = True
#                 else:
#                     # если есть неотгаданные города, то продолжаем игру
#                     sessionStorage[user_id]['game_started'] = True
#                     # номер попытки, чтобы показывать фото по порядку
#                     sessionStorage[user_id]['attempt'] = 1
#                     # функция, которая выбирает город для игры и показывает фото
#                     play_game(res, req)
#             elif 'нет' in req['request']['nlu']['tokens']:
#                 res['response']['text'] = 'Ну и ладно!'
#                 res['end_session'] = True
#             else:
#                 res['response']['text'] = 'Не поняла ответа! Так да или нет?'
#                 res['response']['buttons'] = [
#                     {
#                         'title': 'Да',
#                         'hide': True
#                     },
#                     {
#                         'title': 'Нет',
#                         'hide': True
#                     }
#                 ]
#         else:
#             play_game(res, req)
#
#
# def play_game(res, req):
#     user_id = req['session']['user_id']
#     attempt = sessionStorage[user_id]['attempt']
#     if attempt == 1:
#         # если попытка первая, то случайным образом выбираем город для гадания
#         city = random.choice(list(cities))
#         # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
#         while city in sessionStorage[user_id]['guessed_cities']:
#             city = random.choice(list(cities))
#         # записываем город в информацию о пользователе
#         sessionStorage[user_id]['city'] = city
#         # добавляем в ответ картинку
#         res['response']['card'] = {}
#         res['response']['card']['type'] = 'BigImage'
#         res['response']['card']['title'] = 'Что это за город?'
#         res['response']['card']['image_id'] = cities[city][attempt - 1]
#         res['response']['text'] = 'Тогда сыграем!'
#     else:
#         # сюда попадаем, если попытка отгадать не первая
#         city = sessionStorage[user_id]['city']
#         # проверяем есть ли правильный ответ в сообщение
#         if get_city(req) == city:
#             # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
#             # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
#             res['response']['text'] = 'Правильно! Сыграем ещё?'
#             sessionStorage[user_id]['guessed_cities'].append(city)
#             sessionStorage[user_id]['game_started'] = False
#             return
#         else:
#             # если нет
#             if attempt == 3:
#                 # если попытка третья, то значит, что все картинки мы показали.
#                 # В этом случае говорим ответ пользователю,
#                 # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
#                 # Обратите внимание на этот шаг на схеме.
#                 res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
#                 sessionStorage[user_id]['game_started'] = False
#                 sessionStorage[user_id]['guessed_cities'].append(city)
#                 return
#             else:
#                 # иначе показываем следующую картинку
#                 res['response']['card'] = {}
#                 res['response']['card']['type'] = 'BigImage'
#                 res['response']['card']['title'] = 'Неправильно. Вот тебе дополнительное фото'
#                 res['response']['card']['image_id'] = cities[city][attempt - 1]
#                 res['response']['text'] = 'А вот и не угадал!'
#     # увеличиваем номер попытки доля следующего шага
#     sessionStorage[user_id]['attempt'] += 1
#


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
