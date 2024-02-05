import psycopg2
from psycopg2 import Error
import configparser


class DataBase:
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['params']['user']
    password = config['params']['password']
    host = config['params']['host']
    port = config['params']['port']

    def __init__(self, database=None):
        self._conn = psycopg2.connect(user=self.user,
                                      password=self.password,
                                      host=self.host,
                                      port=self.port,
                                      database=database)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


def add_client(first_name: str, last_name: str, email: str, phones=None):  # func got phones -> tuple like ('123',)
    with DataBase('person_db') as db:
        try:
            sql = '''INSERT INTO person_data (firstname, lastname, email)
                        VALUES (%s, %s, %s);'''
            db.execute(sql, (first_name, last_name, email))
            db.commit()
            if phones:
                sql = '''SELECT person_id from person_data WHERE email = %s;'''
                client_id = db.query(sql, (email,))
                for number in phones:
                    add_phone(client_id[0], number)
        except (Exception, Error) as error:
            print('Error is occurred', error)


def add_phone(client_id, phone):
    with DataBase('person_db') as db:
        try:
            sql = '''INSERT INTO phone_number (person_id, number)
                        VALUES (%s, %s);'''
            db.execute(sql, (client_id, phone))
        except (Exception, Error) as error:
            print('Error is occurred', error)


def change_client(client_id, first_name=None, last_name=None, email=None, phones=None):

    """
    :param client_id: person_id
    :param first_name: firstname
    :param last_name: lastname
    :param email: email
    :param phones: takes tuple like (phone_number1, phone_number2) where 1st is new number and 2nd is replaceable
    """

    dict_args = {'firstname': first_name,
                 'lastname': last_name,
                 'email': email}

    sql = 'UPDATE person_data SET'
    count = len([i for i in dict_args.keys() if dict_args[i]]) - 1
    for i, key in enumerate(dict_args.keys()):
        if dict_args[key]:
            sql += f" {key} = '{dict_args[key]}'"
            if i < count:
                sql += ', '
    sql += f' WHERE person_id = {client_id};'
    with DataBase('person_db') as db:
        try:
            if count > -1:
                db.execute(sql)
                db.commit()
            if phones:
                db.execute('UPDATE phone_number SET number = %s WHERE number = %s', (phones[0], phones[1]))
                db.commit()
        except (Exception, Error) as error:
            print('Error is occurred', error)


def delete_phone(phone):
    phone = (phone,)
    with DataBase('person_db') as db:
        try:
            sql = '''DELETE FROM phone_number
                        WHERE number = %s;'''
            db.execute(sql, phone)
            db.commit()
        except (Exception, Error) as error:
            print('Error is occurred', error)


def delete_client(client_id):
    cl_id = (client_id,)
    with DataBase('person_db') as db:
        try:
            sql = '''delete from phone_number
                        where number = (select number from phone_number pn
                            left join person_data pd on pn.person_id = pd.person_id
                                where pd.person_id = %s);'''
            db.execute(sql, cl_id)
            db.commit()
            sql = '''DELETE FROM person_data
                        WHERE person_id = %s;'''
            db.execute(sql, cl_id)
            db.commit()
        except (Exception, Error) as error:
            print('Error is occurred', error)


def find_client(first_name=None, last_name=None, email=None, phone=None):
    dict_args = {'firstname': first_name,
                 'lastname': last_name,
                 'email': email,
                 'number': phone}
    sql = '''SELECT * FROM person_data pd
                JOIN phone_number pn ON pd.person_id = pn.person_id
                    WHERE '''
    count = len([i for i in dict_args.keys() if dict_args[i]]) - 1
    values = tuple()
    for i, key in enumerate(dict_args.keys()):
        if dict_args[key]:
            values += tuple(dict_args[key])
            sql += f"{key} = '{dict_args[key]}'"
            if i < count:
                sql += ' and '
    sql += ';'
    with DataBase('person_db') as db:
        try:
            db.execute(sql, values)
            print(db.fetchall())
        except (Exception, Error) as error:
            print('Error is occurred', error)
