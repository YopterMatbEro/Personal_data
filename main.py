import psycopg2 as pg
from psycopg2 import Error

with pg.connect(database='personal_date', user='postgres', password='postgres') as conn:
    with conn.cursor() as cur:
        def delete_tables(cursor):
            try:  # сначала настроил перехват исключений, потом подумал, что можно использовать
                # условие IF EXISTS (-_\\). Решил оставить, на случай непредвиденных обстоятельств
                cursor.execute("""  
                    DROP TABLE IF EXISTS clientemail;
                    DROP TABLE IF EXISTS clientphone;
                    DROP TABLE IF EXISTS email;
                    DROP TABLE IF EXISTS phone;
                    DROP TABLE IF EXISTS client;
                    """)
            except (Exception, Error) as error:
                print('Не найдены таблицы в базе данных', error)
        # delete_tables(cur)

        def create_structure_db(cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Client (
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                second_name VARCHAR(40) NOT NULL);
            
                CREATE TABLE IF NOT EXISTS Email (
                mail_id SERIAL PRIMARY KEY,
                email VARCHAR(60) NOT NULL);
            
                CREATE TABLE IF NOT EXISTS Phone (
                number_id SERIAL PRIMARY KEY,
                number DECIMAL DEFAULT 70000000000);
            
                CREATE TABLE IF NOT EXISTS ClientEmail (
                client_id INTEGER REFERENCES Client(client_id),
                mail_id INTEGER REFERENCES Email(mail_id),
                CONSTRAINT client_email PRIMARY KEY (client_id, mail_id));
            
                CREATE TABLE IF NOT EXISTS ClientPhone (
                client_id INTEGER REFERENCES Client(client_id),
                number_id INTEGER REFERENCES Phone(number_id),
                CONSTRAINT client_phone PRIMARY KEY (client_id, number_id));
                """)
            return 'Успешно'
        # testing_db = create_structure_db(cur)
        # print(testing_db)

        def added_new_client(cursor, first_name: str, second_name: str):
            try:
                cursor.execute("""
                    INSERT INTO Client(first_name, second_name)
                    VALUES (%s, %s)
                    """, (first_name, second_name))
                cursor.execute("""
                    SELECT first_name, second_name FROM Client 
                    WHERE first_name=%s AND second_name=%s
                    """, (first_name, second_name))
                result = cur.fetchall()
                print(f'Пользователь "{result[0][0]} {result[0][1]}" добавлен успешно!')
            except(Exception, Error) as error:
                print('Не удалось добавить клиента', error)
        # added_new_client(cur, 'Вася', 'Пупкин')

        # for new commit
        # cur.execute("""
        #     DELETE FROM Client WHERE first_name=%s AND second_name=%s""", ('Вася', 'Пупкин'))