'''The common fixture module'''
# pylint: disable=invalid-name
# pylint: disable=duplicate-code
import os
import pytest
import mysql.connector

def _fetch_database_connection():
    '''Establish a database connection'''
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

def _generate_fake_user_data() -> dict[str, str]:
    '''Generate a fake user data set'''
    return {
        'email': 'yinpinglai@gmail.com',
        'password': 'P@ssw0rd',
        'full_name': 'yinpinglai',
        'secondary_password': '123456',
    }

@pytest.fixture(scope='function')
def fake_user_data() -> dict[str, str]:
    '''Fetch a fake user data set'''
    return _generate_fake_user_data()

@pytest.fixture(scope='class')
def turncate_backend_users():
    '''Clear all backend user records from the testing database'''
    BACKEND_DATABASE = os.environ.get('BACKEND_DATABASE')

    print(f'Turncating all user records from the {BACKEND_DATABASE}.users table.')

    conn = _fetch_database_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"TRUNCATE {BACKEND_DATABASE}.users;"

    cursor.execute(query)
    conn.commit()
    conn.close()

@pytest.fixture(scope='class')
def turncate_users():
    '''Clear all user records from the testing database'''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

    print(f'Turncating all user records from the {MYSQL_DATABASE}.users table.')

    conn = _fetch_database_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"TRUNCATE {MYSQL_DATABASE}.users;"

    cursor.execute(query)
    conn.commit()
    conn.close()

@pytest.fixture(scope='class')
def create_a_testing_user_account():
    '''Create a testing user account'''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

    print(f'Creating a fake user record to the {MYSQL_DATABASE}.users table.')

    conn = _fetch_database_connection()
    cursor = conn.cursor(dictionary=True)

    fake_user = _generate_fake_user_data()
    email = fake_user['email']
    password = fake_user['password']
    full_name = fake_user['full_name']
    secondary_password = fake_user['secondary_password']

    query = (
        f"""
        INSERT INTO {MYSQL_DATABASE}.users
            (password, full_name, email, secondary_password, tfa_secret)
        VALUES
            ('{password}', '{full_name}', '{email}', '{secondary_password}', '654321');
        """
    )

    cursor.execute(query)
    conn.commit()
    conn.close()
