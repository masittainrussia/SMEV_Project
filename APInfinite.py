import sqlite3
import time
import xml.etree.ElementTree as ElTree
from xml.dom import minidom
import requests
import configparser
from functions import generate_xml_requesting_response


# Функция бесконечной отправки запросов на получение ответа от сервиса
def send_request(url, data, headers):
    # Отправка запроса
    response = requests.post(url, data=data, headers=headers)
    # Парсинг полученного ответа для получения OriginalMessageID и MessageId
    response_tree = minidom.parseString(response.content.decode())

    try:
        response_root = response_tree.getElementsByTagName('OriginalMessageID')[0]
        original_message_id = response_root.childNodes[0].nodeValue
        response_root = response_tree.getElementsByTagName('replyToClientId')[0]
        original_client_id = response_root.childNodes[0].nodeValue
        try:
            response_root = response_tree.getElementsByTagName('ns2:FNSResponcePaspINN')[0]
            answer = response_root.getAttribute('КодСоотв')
            connection = sqlite3.connect('Database/fns_requests_database.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * from Requests WHERE response_message_id = ?', (original_message_id,))
            result_string = cursor.fetchall()[0]
            client_id = result_string[1]
            message_id = result_string[3]

            # Запись полученного ответа в лог
            with open(f'Log/second_response.xml', 'wb') as xml_response:
                xml_response.write(response.content)

            # Если id отправленного запроса совпадает с id полученного, то вносим данные в БД
            if original_message_id == message_id and original_client_id == client_id:
                cursor.execute('UPDATE Requests SET xml_result = ? WHERE message_id = ?',
                               (response.text, client_id))
                cursor.execute('UPDATE Requests SET answer = ? WHERE message_id = ?',
                               (answer, client_id))
        except IndexError:
            response_root = response_tree.getElementsByTagName('ns2:docStatus')[0]
            response_answer = response_root.childNodes[0].nodeValue
            connection = sqlite3.connect('Database/passport_requests_database.db')
            cursor = connection.cursor()
            cursor.execute('UPDATE Requests SET document_status_code = ? WHERE message_id = ?',
                           (response_answer, config['DataBase']['MessageId']))
            if int(response_answer) == 301:
                response_root = response_tree.getElementsByTagName('ns2:invalidityReason')[0]
                response_answer = response_root.childNodes[0].nodeValue
                cursor.execute('UPDATE Requests SET invalidity_reason = ? WHERE message_id = ?',
                               (response_answer, config['DataBase']['MessageId']))

        connection.commit()
        connection.close()
    # При возникновнеии ошибки будет получено исключение
    except IndexError:
        print('Ответ еще не сформирован')
    except TypeError:
        print('Ответ еще не сформирован')
    time.sleep(10)


# Функция generate_xml_fnspasp генерирует xml-запрос для проверки наличия ответа от СМЭВ
root = generate_xml_requesting_response()
tree = ElTree.ElementTree(root)
tree.write('Log/second_request.xml', xml_declaration=True, method='xml', encoding='UTF-8')

# Создаем объект парсера конфиг-файла
config = configparser.ConfigParser()
# Читаем конфиг
config.read("fnspassp.config")
# Приводим полученный xml в строковый вид
request_xml = ElTree.tostring(root, encoding='UTF-8')
# Вызываем функцию-поток для отправки запросов
while True:
    send_request(config['SMEV']['GetAdapterURL'], request_xml, {'content-type': 'text/xml'})
