import xml.etree.ElementTree as ElTree
import configparser
import uuid
import re

regex = "^[а-яА-ЯёЁ]+$"
# Создаем объект парсера конфиг-файла
config = configparser.ConfigParser()


def is_it_letters(word):  # Функция проверки слов на наличие кириллицы и отсуттвие прочих символов
    pattern = re.compile(regex)
    return pattern.search(word)


def formated_name(name):  # Функция приводящая получаемые ФИО в красивый вид (ПёТр ==> Пётр)
    name = name.lower()
    return name[0].upper() + name[1:]


def generate_xml_fnspasp(inn, surname, name, patronymic, document_code, issuer_date, num_document, message_id):
    # Читаем конфиг
    config.read("fnspassp.config")
    # Создание корневого элемента
    root = ElTree.Element('soapenv:Envelope')
    # Создание атрибутов корневого элемента и установка их значений
    root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')
    root.set('xmlns:typ', 'urn://x-artefacts-smev-gov-ru/services/service-adapter/types')

    # Создание тэга (1.Тэг)
    sub_root1 = ElTree.SubElement(root, 'soapenv:Header')
    # Создание тэга (2.Тэг)
    sub_root2 = ElTree.SubElement(root, 'soapenv:Body')

    # Создание тэга (2.1.Тэг)
    sub_root3 = ElTree.SubElement(sub_root2, 'tns:ClientMessage')
    # Создание атрибутов тэга и установка их значений
    sub_root3.set('xmlns:n1', 'http://www.altova.com/samplexml/other-namespace')
    sub_root3.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    sub_root3.set('xmlns:tns', 'urn://x-artefacts-smev-gov-ru/services/service-adapter/types')
    sub_root3.set('xsi:schemaLocation', 'urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2')

    # Создание тэга (2.1.1.Тэг)
    sub_root4 = ElTree.SubElement(sub_root3, 'tns:itSystem')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root4.text = config['SMEV']['CodeIS']

    # Создание тэга (2.1.2.Тэг)
    sub_root5 = ElTree.SubElement(sub_root3, 'tns:RequestMessage')
    # Создание тэга (2.1.2.1.Тэг)

    sub_root6 = ElTree.SubElement(sub_root5, 'tns:RequestMetadata')
    # Создание тэга (2.1.2.1.1.Тэг)
    sub_root7 = ElTree.SubElement(sub_root6, 'tns:clientId')
    # Присваивание значения (GUID) созданному тэгу
    sub_root7.text = message_id

    # Создание тэга (2.1.2.1.2.Тэг)
    sub_root8 = ElTree.SubElement(sub_root6, 'tns:createGroupIdentity')

    # Создание тэга (2.1.2.1.2.1.Тэг)
    sub_root9 = ElTree.SubElement(sub_root8, 'tns:FRGUServiceCode')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root9.text = config['SMEV']['ServiceCode']
    # Создание тэга (2.1.2.1.2.2.Тэг)
    sub_root10 = ElTree.SubElement(sub_root8, 'tns:FRGUServiceDescription')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root10.text = config['SMEV']['ServiceDescription']
    # Создание тэга (2.1.2.1.2.3.Тэг)
    sub_root11 = ElTree.SubElement(sub_root8, 'tns:FRGUServiceRecipientDescription')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root11.text = config['SMEV']['ServiceRecipientDescription']

    # Создание тэга (2.1.2.1.3.Тэг)
    sub_root12 = ElTree.SubElement(sub_root6, 'tns:testMessage')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root12.text = config['SMEV']['TestMessage']

    # Создание тэга (2.1.2.2.Тэг)
    sub_root13 = ElTree.SubElement(sub_root5, 'RequestContent')
    # Создание тэга (2.1.2.2.1.Тэг)
    sub_root14 = ElTree.SubElement(sub_root13, 'content')
    # Создание тэга (2.1.2.2.1.1.Тэг)
    sub_root15 = ElTree.SubElement(sub_root14, 'MessagePrimaryContent')

    # Создание тэга (2.1.2.2.1.1.1.Тэг)
    sub_root16 = ElTree.SubElement(sub_root15, 'tns:FNSPaspINNRequest')
    # Создание атрибутов тэга и установка их значений
    sub_root16.set('xmlns:tns', 'urn://x-artefacts-ffns-paspinn-tofns-ru/247-01/4.0.0')
    sub_root16.set('ИННФЛ', inn)

    # Создание тэга (2.1.2.2.1.1.1.1.Тэг)
    sub_root17 = ElTree.SubElement(sub_root16, 'tns:ФИО')
    # Создание атрибутов тэга и установка их значений
    sub_root17.set('FamilyName', formated_name(surname))
    sub_root17.set('FirstName', formated_name(name))
    sub_root17.set('Patronymic', formated_name(patronymic))

    # Создание тэга (2.1.2.2.1.1.1.2.Тэг)
    sub_root18 = ElTree.SubElement(sub_root16, 'tns:ДокУдЛичн')
    # Создание атрибутов тэга и установка их значений
    sub_root18.set('DocumentCode', document_code)
    sub_root18.set('IssuerDate', issuer_date)
    sub_root18.set('SeriesNumber', f"{num_document[:2]} {num_document[2:4]} {num_document[4:]}")
    return root


def generate_xml_passport(surname, name, patronymic, birth_date, series, number, message_id):
    # Читаем конфиг
    config.read("Passport.config")
    # Создание корневого элемента
    root = ElTree.Element('soapenv:Envelope')
    # Создание атрибутов корневого элемента и установка их значений
    root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')
    root.set('xmlns:typ', 'urn://x-artefacts-smev-gov-ru/services/service-adapter/types')

    # Создание тэга (1.Тэг)
    root1 = ElTree.SubElement(root, 'soapenv:Header')
    # Создание тэга (2.Тэг)
    root2 = ElTree.SubElement(root, 'soapenv:Body')

    # Создание корневого элемента
    root3 = ElTree.SubElement(root2, 'tns:ClientMessage')
    # root = ElTree.Element('tns:ClientMessage')
    # Создание атрибутов корневого элемента и установка их значений
    root3.set('xmlns:tns', 'urn://x-artefacts-smev-gov-ru/services/service-adapter/types')
    root3.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root3.set('xmlns:n1', 'http://www.altova.com/samplexml/other-namespace')
    root3.set('xsi:schemaLocation', 'urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.2')

    # Создание тэга (1.Тэг)
    sub_root1 = ElTree.SubElement(root3, 'tns:itSystem')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root1.text = config['SMEV']['CodeIS']

    # Создание тэга (2.Тэг)
    sub_root2 = ElTree.SubElement(root3, 'tns:RequestMessage')
    # Создание тэга (2.1.Тэг)
    sub_root3 = ElTree.SubElement(sub_root2, 'tns:RequestMetadata')

    # Создание тэга (2.1.1.Тэг)
    sub_root4 = ElTree.SubElement(sub_root3, 'tns:clientId')
    # Генерация GUID
    # Присваивание значения (GUID) созданному тэгу
    sub_root4.text = message_id

    # Создание тэга (2.1.2.Тэг)
    sub_root5 = ElTree.SubElement(sub_root3, 'tns:createGroupIdentity')
    # Создание тэга (2.1.2.1.Тэг)
    sub_root6 = ElTree.SubElement(sub_root5, 'tns:FRGUServiceCode')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root6.text = config['SMEV']['ServiceCode']
    # Создание тэга (2.1.2.2.Тэг)
    sub_root7 = ElTree.SubElement(sub_root5, 'tns:FRGUServiceDescription')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root7.text = config['SMEV']['ServiceDescription']
    # Создание тэга (2.1.2.3.Тэг)
    sub_root8 = ElTree.SubElement(sub_root5, 'tns:FRGUServiceRecipientDescription')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root8.text = config['SMEV']['ServiceRecipientDescription']

    # Создание тэга (2.1.3.Тэг)
    sub_root9 = ElTree.SubElement(sub_root3, 'tns:testMessage')
    # Присваивание значения созданному тэгу из конфиг-файла
    sub_root9.text = config['SMEV']['TestMessage']

    # Создание тэга (2.2.Тэг)
    sub_root10 = ElTree.SubElement(sub_root2, 'tns:RequestContent')
    # Создание тэга (2.2.1.Тэг)
    sub_root11 = ElTree.SubElement(sub_root10, 'tns:content')
    # Создание тэга (2.2.1.1.Тэг)
    sub_root12 = ElTree.SubElement(sub_root11, 'tns:MessagePrimaryContent')

    # Создание тэга (2.2.1.1.1.Тэг)
    sub_root13 = ElTree.SubElement(sub_root12, 'tns:request')
    # Создание атрибутов тэга и установка их значений
    sub_root13.set('xmlns:tns', 'urn://mvd/gismu/RFP_ACTUAL_BANK/1.0.0')

    # Создание тэга (2.2.1.1.1.1.Тэг)
    sub_root14 = ElTree.SubElement(sub_root13, 'tns:requestInfo')

    # Создание тэга (2.2.1.1.1.1.1.Тэг)
    sub_root15 = ElTree.SubElement(sub_root14, 'tns:physicalPersonQualifiedNameType')
    # Создание тэга (2.2.1.1.1.1.1.1.Тэг)
    sub_root16 = ElTree.SubElement(sub_root15, 'ns2:familyName')
    # Создание атрибутов тэга и установка их значений
    sub_root16.set('xmlns:ns2', 'urn://mvd/gismu/RFP_ACTUAL_BANK/commons/sovm/1.0.0')
    sub_root16.text = formated_name(surname)
    # Создание тэга (2.2.1.1.1.1.1.2.Тэг)
    sub_root17 = ElTree.SubElement(sub_root15, 'ns2:firstName')
    # Создание атрибутов тэга и установка их значений
    sub_root17.set('xmlns:ns2', 'urn://mvd/gismu/RFP_ACTUAL_BANK/commons/sovm/1.0.0')
    sub_root17.text = formated_name(name)
    # Создание тэга (2.2.1.1.1.1.1.3.Тэг)
    sub_root18 = ElTree.SubElement(sub_root15, 'ns2:patronymic')
    # Создание атрибутов тэга и установка их значений
    sub_root18.set('xmlns:ns2', 'urn://mvd/gismu/RFP_ACTUAL_BANK/commons/sovm/1.0.0')
    sub_root18.text = formated_name(patronymic)

    # Создание тэга (2.2.1.1.1.1.2.Тэг)
    sub_root19 = ElTree.SubElement(sub_root14, 'tns:birthDate')
    sub_root19.text = birth_date

    # Создание тэга (2.2.1.1.1.1.3.Тэг)
    sub_root20 = ElTree.SubElement(sub_root14, 'tns:passportRF')
    # Создание тэга (2.2.1.1.1.1.3.1.Тэг)
    sub_root21 = ElTree.SubElement(sub_root20, 'ns2:series')
    sub_root21.set('xmlns:ns2', 'urn://mvd/gismu/RFP_ACTUAL_BANK/commons/sovm/1.0.0')
    sub_root21.text = series
    # Создание тэга (2.2.1.1.1.1.3.2.Тэг)
    sub_root22 = ElTree.SubElement(sub_root20, 'ns2:number')
    sub_root22.set('xmlns:ns2', 'urn://mvd/gismu/RFP_ACTUAL_BANK/commons/sovm/1.0.0')
    sub_root22.text = number
    return root


def generate_xml_requesting_response():
    # Читаем конфиг
    config.read("fnspassp.config")

    root = ElTree.Element('soapenv:Envelope')
    # Создание атрибутов корневого элемента и установка их значений
    root.set('xmlns:soapenv', 'http://schemas.xmlsoap.org/soap/envelope/')
    root.set('xmlns:typ', 'urn://x-artefacts-smev-gov-ru/services/service-adapter/types')
    # Создание тэга (1.Тэг)
    sub_root1 = ElTree.SubElement(root, 'soapenv:Header')
    # Создание тэга (2.Тэг)
    sub_root2 = ElTree.SubElement(root, 'soapenv:Body')
    # Создание тэга (2.1.Тэг)
    sub_root3 = ElTree.SubElement(sub_root2, 'typ:MessageQuery')
    sub_root4 = ElTree.SubElement(sub_root3, 'typ:itSystem')
    sub_root4.text = config['SMEV']['CodeIS']
    sub_root5 = ElTree.SubElement(sub_root3, 'typ:messageTypeCriteria')
    sub_root5.text = config['SMEV']['MessageType']
    return root
