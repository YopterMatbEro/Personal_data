import psycopg2 as pg
from psycopg2 import Error


def yes_or_no(question):
    response = ''
    while response not in ('да', 'нет'):
        print(question)
        response = input('("да" или "нет"): ')
    return response


# Удаление таблиц
def delete_tables(cursor):
    try:
        cursor.execute("""  
            DROP TABLE IF EXISTS clientemail;
            DROP TABLE IF EXISTS email;
            DROP TABLE IF EXISTS phone;
            DROP TABLE IF EXISTS client;
            """)
        print('Успешно удалено')
    except (Exception, Error) as error:
        print('Непредвиденная ошибка', error)


# Создание структуры БД
def create_structure_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Client (
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        second_name VARCHAR(40) NOT NULL);

        CREATE TABLE IF NOT EXISTS Email (
        mail_id SERIAL PRIMARY KEY,
        email VARCHAR(120) NOT NULL);

        CREATE TABLE IF NOT EXISTS Phone (
        phone_id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES Client(client_id),
        number DECIMAL DEFAULT 70000000000);

        CREATE TABLE IF NOT EXISTS ClientEmail (
        client_id INTEGER REFERENCES Client(client_id),
        mail_id INTEGER REFERENCES Email(mail_id),
        CONSTRAINT client_email PRIMARY KEY (client_id, mail_id));
        """)
    print('Успешно')


# Добавление нового клиента
def add_client(cursor, first_name: str, second_name: str, email: str):
    try:
        cursor.execute("""
            INSERT INTO Client(first_name, second_name)
            VALUES (%s, %s)
            """, (first_name, second_name))
        cursor.execute("""
            SELECT client_id, first_name, second_name FROM Client 
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        client = cursor.fetchall()

        phone_or_without = yes_or_no('Будете указывать номер телефона?')
        if phone_or_without == 'да':
            number = int(input('Введите номер телефона: '))
            cursor.execute("""
                INSERT INTO Phone(client_id, number)
                VALUES (%s, %s)
                """, (client[0][0], number))
        else:
            cursor.execute("""
                INSERT INTO Phone(client_id, number)
                VALUES (%s, DEFAULT)
                """, (client[0][0],))
        cursor.execute("""
            INSERT INTO Email(email)
            VALUES (%s)
            """, (email,))

        cursor.execute("""
            SELECT mail_id FROM Email WHERE email=%s
            """, (email,))
        mail = cursor.fetchall()
        cursor.execute("""
            INSERT INTO ClientEmail(client_id, mail_id)
            VALUES (%s, %s)
            """, (client[0][0], mail[0][0]))
        print(f'Клиент "{client[0][1]} {client[0][2]}" добавлен успешно!')
    except(Exception, Error) as error:
        print('Не удалось добавить клиента', error)


# Добавление телефона существующему клиенту
def add_phone(cursor, first_name: str, second_name: str, number):
    try:
        # проверка на наличие клиента
        cursor.execute("""
            SELECT client_id, first_name, second_name FROM Client
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        sel = cursor.fetchall()

        if sel[0][1] == first_name and sel[0][2] == second_name:
            # если клиент есть, добавить его номер телефона
            cursor.execute("""
                INSERT INTO Phone(client_id, number)
                VALUES (%s, %s)
                """, (sel[0][0], number))
            # финальная проверка на добавление в БД необходимого нам номера
            cursor.execute("""
                SELECT client_id, number FROM Phone 
                WHERE client_id=%s AND number=%s
                """, (sel[0][0], number))
            result = cursor.fetchall()
            print(f'Клиенту "{first_name} {second_name}" успешно добавлен номер: {result[0][1]}')
        else:
            print('Клиент не найден. Проверьте корректность введённых данных')
    except(Exception, Error) as error:
        print('Операция завершена с ошибкой', error)


# Обновление данных клиента
def update_client(cursor):
    try:
        print('Для изменения данных')
        first_name = input('Укажите имя клиента: ')
        second_name = input('Укажите фамилию клиента: ')
        cursor.execute("""
            SELECT first_name, second_name FROM Client
            WHERE first_name=%s AND second_name=%s
            """, (first_name.capitalize(), second_name.capitalize()))
        found_client = cursor.fetchall()

        if found_client[0][0] == first_name and found_client[0][1] == second_name:
            print(''' Клиент найден.\n
                Чтобы изменить данные в БД Вам необходимо указать ключи к данным,
                которые желаете редактировать
                Внимание!!! ключи указывать строго через пробел и без знаков препинания!
                Например: и ф т
                где:
                и - имя;
                ф - фамилия;
                т - телефон;
                е - емейл.
                ''')
            response = ''
            new_first_name = ''
            new_second_name = ''
            new_email = ''

            while response.lower().split() not in ['и', 'ф', 'т', 'е']:
                response = input('Введите необходимый(е) ключ(и): ')

            for key in response.lower().split():
                if key == 'и':
                    new_first_name = input('Введите новое имя: ').capitalize()
                elif key == 'ф':
                    new_second_name = input('Введите новую фамилию: ').capitalize()
                elif key == 'т':
                    print('Если Вы хотите заменить номер телефона введите "да", если добавить - "нет"', end='')
                    change_or_add = yes_or_no('Ваш ответ: ').lower()
                    new_phone = int(input('Введите новый номер телефона: '))
                    if change_or_add == 'нет':
                        add_phone(cursor, first_name, second_name, new_phone)
                    else:
                        old_number = int(input('Введите старый номер: '))
                        cursor.execute("""
                            SELECT number FROM Phone WHERE number=%s
                            """, (old_number,))
                        tmp = cursor.fetchall()

                        if tmp[0][0] == old_number:
                            cursor.execute("""
                                UPDATE Phone SET number=%s WHERE number=%s
                                """, (new_phone, old_number))
                            cursor.execute("""
                                SELECT phone_id, number FROM Phone WHERE number=%s
                                """, (new_phone,))
                            phone_result = cursor.fetchall()
                            print(f'Теперь под id: {phone_result[0][0]} находится номер: {phone_result[0][1]}')
                        else:
                            print('Такого номера нет в БД, можно добавить новый номер вместо замены')
                            need_add_phone = yes_or_no('Добавляем?')
                            if need_add_phone == 'да':
                                add_phone(cursor, first_name, second_name, new_phone)
                            else:
                                print('Изменений среди телефонных номеров клиента не задано.')
                elif key == 'е':
                    new_email = input('Введите новый емейл: ')
                else:
                    print(f'Ключ {key} не подходит ни к одному из предложенных вариантов.')

            if new_first_name:
                cursor.execute("""
                    UPDATE Client SET first_name=%s WHERE first_name=%s
                    """, (new_first_name, first_name))
            if new_second_name:
                cursor.execute("""
                    UPDATE Client SET second_name=%s WHERE second_name=%s
                    """, (new_second_name, second_name))
            if new_email:
                cursor.execute("""
                    SELECT email FROM Client c
                    JOIN ClientEmail ce ON ce.client_id = c.client_id
                    JOIN Email e on e.mail_id = ce.mail_id
                    WHERE first_name=%s AND second_name=%s
                    """, (first_name, second_name))
                old_email = cursor.fetchall()
                cursor.execute("""
                    UPDATE Email SET email=%s WHERE email=%s
                    """, (new_email, old_email[0][0]))
        else:
            print('Клиент не найден.')
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)



# Удаление клиента
# cur.execute("""
#     DELETE FROM Client WHERE first_name=%s AND second_name=%s""", ('Вася', 'Пупкин'))


with pg.connect(database='personal_data', user='postgres', password='MAXpayne23018975') as conn:
    with conn.cursor() as cur:

        # delete_tables(cur)

        # create_structure_db(cur)

        # add_client(cur, 'Алёша', 'Попович', 'Alenushka1love@ooo-boratyr.ru')
        # add_client(cur, 'Илья', 'Муромец', 'Ilya33@ooo-boratyr.ru')
        # add_client(cur, 'Добрыня', 'Никитич', 'WhereMySyrname@ooo-boratyr.ru')

        # add_phone(cur, 'Вася', 'Пупкин', 79645437821)

        # update_client(cur)