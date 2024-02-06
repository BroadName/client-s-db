import configparser
import psycopg2
from psycopg2 import Error


def create_db():
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['params']['user']
    password = config['params']['password']
    host = config['params']['host']
    port = config['params']['port']

    try:
        connection = psycopg2.connect(user=user, password=password, host=host, port=port)
        sql_create_database = f'CREATE DATABASE person_db'
        cursor = connection.cursor()
        connection.autocommit = True
        cursor.execute(sql_create_database)
        print('person_data_db is created!')
        cursor.close()
        connection.close()
    except (Exception, Error) as e:
        print('Error is occurred with PostgreSQL', e)

    try:
        with psycopg2.connect(user=user, password=password, host=host, port=port, database='person_db') as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                sql_create_table = '''CREATE TABLE IF NOT EXISTS person_data (
                                        person_id SERIAL PRIMARY KEY,
                                        firstname VARCHAR(100) NOT NULL,
                                        lastname VARCHAR(100) NOT NULL,
                                        email VARCHAR(255) NULL UNiQUE);'''
                cursor.execute(sql_create_table)
                print('The person_data table is created!')
                sql_create_table = '''CREATE TABLE IF NOT EXISTS phone_number (
                                        phone_id SERIAL PRIMARY KEY,
                                        number VARCHAR(50) NULL UNIQUE,
                                        person_id INT NOT NULL,
                                        FOREIGN KEY(person_id) REFERENCES person_data(person_id));
                                        '''
                cursor.execute(sql_create_table)
                print('The phone_number table is created!')
    except (Exception, Error) as e:
        print('Error is occurred with PostgreSQL', e)


create_db()