import json
from flask import Flask, request
import xml.etree.ElementTree as ElTree
from xml.dom import minidom
import sqlite3
import uuid
from datetime import date
import requests
import configparser
from functions import is_it_letters, generate_xml_fnspasp, generate_xml_passport


app = Flask(__name__)


@app.route('/fnspassportcheker', methods=['POST'])
def xml_listener():
    # Запись данных в переменную из полученного запроса json somekey ключи на латиницу
    json_data = request.json
    # Генерация GUID
    message_id = str(uuid.uuid4())
    # Создаем объект парсера конфиг-файла
    config = configparser.ConfigParser()
    # Функция для сохранения регистра ключей
    config.optionxform = str
    # Читаем конфиг
    config.read("fnspassp.config")

    # Проверка полученных из запроса данных на корректность
    if json_data['DocumentCode'] == '21':
        inn = json_data['INN'].isdigit() and len(json_data['INN']) == 12
        surname = is_it_letters(json_data['Surname'])
        name = is_it_letters(json_data['Name'])
        patronymic = is_it_letters(json_data['Patronymic'])
        issuer_date = date.fromisoformat(json_data['IssuerDate']) <= date.today()
        num_document = json_data['DocumentNumber'].isdigit() and len(json_data['DocumentNumber']) == 10
        client_is_actual = (inn and surname and name and patronymic and issuer_date and num_document)
    else:
        return {'Error': 'Incorrect document code'}

    # Если проверка данных пройдена, то формируется итоговый XML и отправляется в СМЭВ
    if client_is_actual:
        # Функция generate_xml_fnspasp генерирует xml для проверки соотвествия ИНН и паспорта
        root = generate_xml_fnspasp(json_data['INN'], json_data['Surname'], json_data['Name'],
                                    json_data['Patronymic'], json_data['DocumentCode'], json_data['IssuerDate'],
                                    json_data['DocumentNumber'], message_id)
        tree = ElTree.ElementTree(root)
        tree.write(f'Log/first_request.xml', xml_declaration=True, method='xml', encoding='UTF-8')

        # Получение ответа от СМЭВ и его запись в log
        data = ElTree.tostring(root, encoding='UTF-8')
        try:
            response = requests.post(config['SMEV']['AdapterURL'], data=data, headers={'content-type': 'text/xml'})
        except TimeoutError:
            return {'Error': 'Timeout error'}

        with open('Log/first_response.xml', 'wb') as xml_response:
            xml_response.write(response.content)

        # Парсинг полученного ответа для получения MessageId под которым зарегестрирован запрос
        response_tree = minidom.parseString(response.content.decode())
        response_root = response_tree.getElementsByTagName('MessageId')[0]
        response_id = response_root.childNodes[0].nodeValue

        # Подключение к базе данных и запись в нее полученных на данный момент данных
        try:
            connection = sqlite3.connect('Database/requests_database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Requests (message_id, json_received, response_message_id) VALUES (?, ?, ?)',
                           (message_id, json.dumps(json_data), response_id))
            connection.commit()
            connection.close()
        except TypeError:
            return {'Error': 'Wrong data type'}
        except ValueError:
            return {'Error': 'Wrong value'}

        return ''

    else:  # Вывод исключений при получении неверных данных
        if not inn:
            return {'Error': 'Incorrect INN'}
        if not surname:
            return {'Error': 'Incorrect surname'}
        if not name:
            return {'Error': 'Incorrect name'}
        if not patronymic:
            return {'Error': 'Incorrect patronymic'}
        if not num_document:
            return {'Error': 'Incorrect document number'}
        if not issuer_date:
            return {'Error': 'Incorrect issuer date'}


@app.route('/passportcheсker', methods=['POST'])
def xml_listener():
    # Запись данных в переменную из полученного запроса
    json_data = request.json
    # Генерация GUID
    message_id = str(uuid.uuid4())
    # Создаем объект парсера конфиг-файла
    config = configparser.ConfigParser()
    # Функция для сохранения регистра ключей
    config.optionxform = str
    # Читаем конфиг
    config.read("Passport.config")

    # Проверка полученных из запроса данных на корректность
    surname = is_it_letters(json_data['Surname'])
    name = is_it_letters(json_data['Name'])
    patronymic = is_it_letters(json_data['Patronymic'])
    birth_date = date.fromisoformat(json_data['BirthDate']) <= date.today()
    series = json_data['Series'].isdigit() and len(json_data['Series']) == 4
    number = json_data['Number'].isdigit() and len(json_data['Number']) == 6
    client_is_actual = (surname and name and patronymic and birth_date and series and number)

    # Если проверка данных пройдена, то формируется итоговый XML и отправляется в СМЭВ
    if client_is_actual:
        # Вызов функции generate_xml_passport, которая возвращает готовый xml-запрос на проверку паспорта
        root = generate_xml_passport(json_data['Surname'], json_data['Name'], json_data['Patronymic'],
                                     json_data['BirthDate'], json_data['Series'], json_data['Number'], message_id)
        # Создание дерева xml и его запись в log
        tree = ElTree.ElementTree(root)
        tree.write('Log/first_request.xml', xml_declaration=True, method='xml', encoding='UTF-8')

        # Приведение xml к строковому виду и отправление запроса
        data = ElTree.tostring(root, xml_declaration=True, encoding='UTF-8')
        try:
            response = requests.put(config['SMEV']['AdapterURL'], data=data, headers={'content-type': 'text/xml'})
        except TimeoutError:
            return {'Error': 'Timeout error'}

        #  Запись ответа от сервиса в log
        file = open('Log/first_response.xml', 'wb')
        file.write(response.content)
        file.close()

        # Парсинг полученного ответа для получения MessageId
        response_tree = minidom.parseString(response.content.decode())
        response_root = response_tree.getElementsByTagName('MessageId')[0]
        response_id = response_root.childNodes[0].nodeValue

        # Подключение к базе данных и запись в нее полученных на данном этапе данных
        try:
            connection = sqlite3.connect('Database/fns_requests_database.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Requests (message_id, json_received, response_message_id) VALUES '
                           '(?, ?, ?)', (message_id, json_data, response_id))
            connection.commit()
            connection.close()
        except TypeError:
            return {'Error': 'Wrong data type'}
        except ValueError:
            return {'Error': 'Wrong value'}

        return ''

    else:  # Вывод исключений при получении неверных данных
        if not surname:
            return {'Error': 'Incorrect surname'}
        if not name:
            return {'Error': 'Incorrect name'}
        if not patronymic:
            return {'Error': 'Incorrect patronymic'}
        if not birth_date:
            return {'Error': 'Incorrect birth_date'}
        if not series:
            return {'Error': 'Incorrect passport series'}
        if not number:
            return {'Error': 'Incorrect passport number'}


# Костыль для выполнения кода только при случае его вызова
if __name__ == '__main__':
    # Указание слушать любые IP-адреса на этом хосте
    app.run(host='0.0.0.0')

###
# curl -X POST -H "Content-Type: application/json" -d "{"""INN""":"""type here""", """Surname""": """type here""", """Name""": """type here""", """Patronymic""": """type here""", """DocumentCode""": """21""", """IssuerDate""": """YYYY-MM-DD""", """DocumentNumber""": """1111111111"""}" http://127.0.0.1:5000/fnspassportcheker
# curl -X POST -H "Content-Type: application/json" -d "{"""Surname""":"""type here""", """Name""":"""type here""", """Patronymic""":"""type here""", """BirthDate""":"""YYYY-MM-DD""", """Series""":"""type here 1111""", """Number""":"""type here 111111"""}" http://127.0.0.1:5000/passportcheсker