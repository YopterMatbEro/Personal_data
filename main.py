import psycopg2 as pg
from psycopg2 import Error
import configparser


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
        if found_client[1] == first_name and found_client[2] == second_name:
            # если найден клиент, проверить наличие номера
            cursor.execute("""
                SELECT number FROM Phone p
                JOIN client c ON p.client_id = c.client_id
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name))
            found_number = cursor.fetchall()[0]
            if found_number[0] == phone:
                print('Этот номер уже определен у клиента')
            elif found_number[0] == 70000000000:  # заменить дефолтный на фактический
                cursor.execute("""
                    UPDATE Phone SET number=%s WHERE client_id=%s
                    """, (phone, found_client[0]))
                conn.commit()
            else:
                cursor.execute("""
                    INSERT INTO Phone(client_id, number)
                    VALUES (%s, %s)
                    """, (found_client[0], phone))
                conn.commit()
            cursor.execute("""
                SELECT number FROM Phone 
                WHERE client_id=%s AND number=%s
                """, (found_client[0], phone))
            result = cursor.fetchall()[0]
            print(f'Клиенту "{first_name} {second_name}" успешно добавлен номер: {result[0]}')
        else:  # Помогите Даше найти клиента... (・_・;)
            print('Клиент не найден. Проверьте корректность введённых данных и попробуйте снова.')
    except(Exception, Error) as error:
        print('Операция завершена с ошибкой', error)


# Обновление данных клиента
def update_client(cursor, first_name=None, second_name=None, phone=None, email=None):
    """
    Для изменения данных о клиенте необходимо указать нужный аттрибут и прописать ему явное
    актуальное значение, хранящееся в БД:
    :param first_name = имя
    :param second_name = фамилия
    :param phone = номер телефона (цифрами)
    :param email = адрес электронной почты по шаблону: adress@pochta.domen
    """
    try:
        if first_name and second_name:
            cursor.execute("""
                SELECT first_name, second_name FROM Client
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name))
            client_exist = cursor.fetchall()
            if not client_exist:
                print('Клиента с таким именем не существует. Проверьте корректность введённых данных и попробуйте снова.')
            else:
                new_first_name = input('Какое имя хотите установить? ').capitalize()
                new_second_name = input('Какую фамилию хотите установить? ').capitalize()
                cursor.execute("""
                    UPDATE Client SET first_name=%s, second_name=%s WHERE first_name=%s AND second_name=%s
                    """, (new_first_name, new_second_name, first_name, second_name))
                conn.commit()
                print('Успешно')
        elif first_name:
            second_name = input('Для поиска клиента в БД, укажите фамилию клиента: ').capitalize()
            cursor.execute("""
                SELECT first_name, second_name FROM Client
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name))
            client_exist = cursor.fetchall()
            if not client_exist:
                print('Клиента с таким именем не существует. Проверьте корректность введённых данных и попробуйте снова.')
            else:
                new_first_name = input('На какое имя хотите сменить? ').capitalize()
                cursor.execute("""
                    UPDATE Client SET first_name=%s WHERE first_name=%s AND second_name=%s
                    """, (new_first_name, first_name, second_name))
                conn.commit()
                print('Успешно')
        elif second_name:
            first_name = input('Для поиска клиента в БД, укажите имя клиента: ').capitalize()
            cursor.execute("""
                SELECT first_name, second_name FROM Client
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name))
            client_exist = cursor.fetchall()
            if not client_exist:
                print('Клиента с таким именем не существует. Проверьте корректность введённых данных и попробуйте снова.')
            else:
                new_second_name = input('На какую фамилию хотите сменить? ').capitalize()
                cursor.execute("""
                    UPDATE Client SET second_name=%s WHERE first_name=%s AND second_name=%s
                    """, (new_second_name, first_name, second_name))
                conn.commit()
                print('Успешно')
        if phone:
            cursor.execute("""
                SELECT number FROM Phone WHERE number=%s
                """, (phone,))
            number_exists = cursor.fetchall()
            if not number_exists:
                print('Такого номера нет ни у одного клиента. Проверьте корректность введённых данных и попробуйте снова.')
            else:
                new_number = int(input('На какой номер хотите сменить? '))
                cursor.execute("""
                    UPDATE Phone SET number=%s WHERE number=%s
                    """, (new_number, phone))
                conn.commit()
                print('Успешно')
        if email:
            cursor.execute("""
                SELECT email FROM Email WHERE email=%s
                """, (email,))
            email_exists = cursor.fetchall()
            if not email_exists:
                print('Такой почты нет ни у одного клиента. Проверьте корректность введённых данных и попробуйте снова.')
            else:
                new_email = input('На какой адрес хотите сменить почту? ')
                cursor.execute("""
                    UPDATE Email SET email=%s WHERE email=%s
                    """, (new_email, email))
                conn.commit()
                print('Успешно')
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)


# Удаление телефона для существующего клиента
def delete_phone_number(cursor, first_name: str, second_name: str, phone):
    try:
        cursor.execute("""
            SELECT number FROM Phone p
            JOIN Client c ON c.client_id = p.client_id
            WHERE first_name=%s AND select_name=%s
            """, (first_name, second_name))
        phone_exists = cursor.fetchall()
        if not phone_exists:
            print('У этого клиента нет такого номера телефона. Проверьте корректность введённых данных и попробуйте снова.')
        else:
            cursor.execute("""
                UPDATE Phone SET number=DEFAULT WHERE number=%s
                """, (phone,))
            conn.commit()
            print('Успешно')
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)


# Удаление клиента
def delete_client(cursor, first_name, second_name):
    try:
        cursor.execute("""
            SELECT client_id FROM Client
            WHERE first_name=%s AND second_name=%s
            """, (first_name, second_name))
        client_id = cursor.fetchone()
        if not client_id:
            print('Клиента с таким именем не найдено. Проверьте корректность введённых данных и попробуйте снова.')
        else:
            cursor.execute("""
                DELETE FROM Phone WHERE client_id=%s
                """, (client_id[0],))
            cursor.execute("""
                DELETE FROM Email WHERE client_id=%s
                """, (client_id[0],))
            cursor.execute("""
                DELETE FROM Client WHERE client_id=%s
                """, (client_id[0],))
            conn.commit()
            print(f'{first_name} {second_name} стёрт с лица БД!')
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)


# Поиск клиента по его данным
def find_client(cursor, first_name=None, second_name=None, phone=None, email=None):
    """
    Для поиска клиента необходимо указать нужный аттрибут и прописать ему явное
    актуальное значение, хранящееся в БД:
    :param first_name = имя
    :param second_name = фамилия
    :param phone = номер телефона (цифрами)
    :param email = адрес электронной почты по шаблону: adress@pochta.domen
    """
    try:
        if first_name and second_name:
            cursor.execute("""
                SELECT first_name, second_name, number, email FROM Client c
                JOIN Phone p ON c.client_id = p.client_id
                JOIN Email e ON c.client_id = e.client_id
                WHERE first_name=%s AND second_name=%s
                """, (first_name, second_name))
            client_exist = cursor.fetchall()
            if not client_exist:
                print('Клиента с таким именем не существует. Проверьте корректность введённых данных и попробуйте снова.')
                print('Либо укажите дополнительные данные.')
            else:
                print(f'Информация:')
                print(*client_exist[0])
        elif phone:
            cursor.execute("""
                SELECT first_name, second_name, number, email FROM Client c
                JOIN Phone p ON c.client_id = p.client_id
                JOIN Email e ON c.client_id = e.client_id
                WHERE number=%s
                """, (phone,))
            client_exist = cursor.fetchall()
            if not client_exist:
                print(
                    'Клиента с такой номером телефона не существует. Проверьте корректность введённых данных и попробуйте снова.')
                print('Либо укажите дополнительные данные.')
            else:
                print(f'Информация:')
                print(*client_exist[0])
        elif email:
            cursor.execute("""
                SELECT first_name, second_name, number, email FROM Client c
                JOIN Phone p ON c.client_id = p.client_id
                JOIN Email e ON c.client_id = e.client_id
                WHERE email=%s
                """, (email,))
            client_exist = cursor.fetchall()
            if not client_exist:
                print(
                    'Клиента с таким адресом почты не существует. Проверьте корректность введённых данных и попробуйте снова.')
                print('Либо укажите дополнительные данные.')
            else:
                print(f'Информация:')
                print(*client_exist[0])
    except(Exception, Error) as error:
        print('Непредвиденная ошибка', error)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    with pg.connect(
            database=config.get('sql', 'db'), user=config.get('sql', 'user'), password=config.get('sql', 'password')
    ) as conn:
        with conn.cursor() as cur:

            delete_tables(cur)

            # create_structure_db(cur)

            # add_client(cur, 'Алёша', 'Попович', 'Alenushka1love@ooo-bogatyr.ru', phone=79001112233)
            # add_client(cur, 'Илья', 'Муромец', 'Ilya33@ooo-bogatyr.ru')
            # add_client(cur, 'Добрыня', 'Никитич', 'WhereIsMySyrname@ooo-bogatyr.ru')

            # add_phone(cur, 'Илья', 'Муромец', 88005553535)  # замена дефолтного номера
            # add_phone(cur, 'Алёша', 'Попович', 87772281488)  # добавление номера

            # update_client(cur, first_name='Илья', second_name='Муромец')
            # update_client(cur, first_name='Алёша', phone=79001112233)
            # update_client(cur, second_name='Никитич', email='WhereIsMySyrname@ooo-bogatyr.ru')

            # delete_client(cur, 'Алёша', 'Попович')
            # delete_client(cur, 'Илья', 'Муромец')
            # delete_client(cur, 'Добрыня', 'Никитич')

            # find_client(cur, first_name='Алёша', second_name='Попович')
            # find_client(cur, phone=88005553535)
            # find_client(cur, email='WhereIsMySyrname@ooo-bogatyr.ru')

            # select из базы для проверки изменений в БД (я чекал изменения в Dbeaver)
            # try:
            #     cur.execute("""
            #         SELECT c.client_id, first_name, second_name, email, number  FROM client c
            #         LEFT JOIN email e ON e.client_id = c.client_id
            #         LEFT JOIN phone p ON p.client_id = c.client_id
            #         """)
            #     print(*cur.fetchall(), sep='\n')
            # except(Exception, Error) as error:
            #     print('Данные в БД отсутствуют:', error)
