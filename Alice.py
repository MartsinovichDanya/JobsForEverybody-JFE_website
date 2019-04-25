from flask import Flask, request
import logging
import json
import random


from DB import DB
from Models import AliceUserModel, VacModel, ParamModel

app = Flask(__name__)
db = DB('alice_jfe.db')

logging.basicConfig(level=logging.INFO)


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
        aum.insert(user_id, None, None)
        print(aum.get(user_id))
        return

    if not aum.get(user_id)[1]:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            aum.update_name(user_id, first_name)
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}.'

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
#
# def get_city(req):
#     # перебираем именованные сущности
#     for entity in req['request']['nlu']['entities']:
#         # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
#         if entity['type'] == 'YANDEX.GEO':
#             # возвращаем None, если не нашли сущности с типом YANDEX.GEO
#             return entity['value'].get('city', None)


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
