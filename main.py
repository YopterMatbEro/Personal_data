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
        email VARCHAR(120) NOT NULL,
        client_id INTEGER REFERENCES Client(client_id));

        CREATE TABLE IF NOT EXISTS Phone (
        phone_id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES Client(client_id),
        number DECIMAL DEFAULT 70000000000);
        """)
    print('Успешно')


# Добавление нового клиента
def add_client(cursor, first_name: str, second_name: str, email: str, phone=70000000000):
    try:
        cursor.execute("""
            INSERT INTO Client(first_name, second_name)
            VALUES (%s, %s)
            """, (first_name, second_name))
        cursor.execute("""
            SELECT client_id, first_name, second_name FROM Client 
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        client = cursor.fetchall()[0]

        if phone != 70000000000:
            cursor.execute("""
                INSERT INTO Phone(client_id, number)
                VALUES (%s, %s)
                """, (client[0], phone))
        else:
            cursor.execute("""
                INSERT INTO Phone(client_id, number)
                VALUES (%s, DEFAULT)
                """, (client[0],))
        cursor.execute("""
            INSERT INTO Email(email, client_id)
            VALUES (%s, %s)
            """, (email, client[0]))
        conn.commit()
        print(f'Клиент "{client[1]} {client[2]}" добавлен успешно!')
    except(Exception, Error) as error:
        print('Не удалось добавить клиента', error)


# Добавление телефона существующему клиенту
def add_phone(cursor, first_name: str, second_name: str, phone):
    try:
        # проверка на наличие клиента
        cursor.execute("""
            SELECT client_id, first_name, second_name FROM Client
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        found_client = cursor.fetchall()[0]
        print(found_client)
        if found_client[1] == first_name and found_client[2] == second_name:
            # если найден клиент, проверить наличие номера
            cursor.execute("""
                SELECT number FROM Phone p
                JOIN client c ON p.client_id = c.client_id
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name, phone))
            found_number = cursor.fetchall()[0]
            if found_number[0] == phone:
                print('Этот номер уже определен у клиента')
            elif found_number[0] == 70000000000:  # заменить дефолтный на фактический
                cursor.execute("""
                    UPDATE Phone SET number=%s WHERE client_id=%s
                    """, (phone, found_client[0]))
            else:
                cursor.execute("""
                    INSERT INTO Phone(client_id, number)
                    VALUES (%s, %s)
                    """, (found_client[0], phone))
            cursor.execute("""
                SELECT number FROM Phone 
                WHERE client_id=%s AND number=%s
                """, (found_client[0], phone))
            result = cursor.fetchall()[0]
            print(f'Клиенту "{first_name} {second_name}" успешно добавлен номер: {result[0]}')
        else:  # помогите Даше найти клиента... (・_・;)
            print('Клиент не найден. Проверьте корректность введённых данных')
    except(Exception, Error) as error:
        print('Операция завершена с ошибкой', error)


# Обновление данных клиента
def update_client(cursor):
    try:
        print('Для изменения данных')
        first_name = input('Укажите имя клиента: ').capitalize()
        second_name = input('Укажите фамилию клиента: ').capitalize()
        cursor.execute("""
            SELECT first_name, second_name FROM Client
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        found_client = cursor.fetchall()[0]

        if found_client[0] == first_name and found_client[1] == second_name:
            print(''' Клиент найден.\n
                Чтобы определить изменяемые данные в БД Вам необходимо указать ключи,
                Внимание!!! 
                ключи указывать строго кириллицей, через пробел и без знаков препинания!
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
                        tmp = cursor.fetchall()[0]

                        if tmp[0] == old_number:
                            cursor.execute("""
                                UPDATE Phone SET number=%s WHERE number=%s
                                """, (new_phone, old_number))
                            cursor.execute("""
                                SELECT phone_id, number FROM Phone WHERE number=%s
                                """, (new_phone,))
                            phone_result = cursor.fetchall()[0]
                            print(f'Теперь под id: {phone_result[0]} находится номер: {phone_result[1]}')
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
                    JOIN Email e on e.client_id = c.client_id
                    WHERE first_name=%s AND second_name=%s
                    """, (first_name, second_name))
                old_email = cursor.fetchall()[0]
                cursor.execute("""
                    UPDATE Email SET email=%s WHERE email=%s
                    """, (new_email, old_email[0]))
        else:
            print('Клиент не найден.')
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)



# Удаление клиента
# cur.execute("""
#     DELETE FROM Client WHERE first_name=%s AND second_name=%s""", ('Вася', 'Пупкин'))


with pg.connect(database='personal_data', user='postgres', password='postgres') as conn:
    with conn.cursor() as cur:

        # delete_tables(cur)

        # create_structure_db(cur)

        # add_client(cur, 'Алёша', 'Попович', 'Alenushka1love@ooo-boratyr.ru', phone=79645437821)
        # add_client(cur, 'Илья', 'Муромец', 'Ilya33@ooo-boratyr.ru')
        # add_client(cur, 'Добрыня', 'Никитич', 'WhereIsMySyrname@ooo-boratyr.ru')

        add_phone(cur, 'Илья', 'Муромец', 88005553535)  # замена дефолтного номера
        add_phone(cur, 'Алёша', 'Попович', 87772281488)  # добавление номера

        # update_client(cur)