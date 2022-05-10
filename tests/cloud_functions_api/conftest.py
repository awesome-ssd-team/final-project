'''The common fixture module'''
# pylint: disable=invalid-name
# pylint: disable=duplicate-code
import os
import pytest
import mysql.connector

@pytest.fixture(scope='function')
def fake_user_data() -> dict[str, str]:
    '''Generate a fake user data set'''
    return {
        'full_name': 'yinpinglai',
        'email': 'yinpinglai@gmail.com',
        'password': 'P@ssw0rd',
        'secondary_password': '123456',
    }

@pytest.fixture(scope='class')
def turncate_users():
    '''Clear all user records from the testing database'''

    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

    cursor = conn.cursor(dictionary=True)

    query = f"TRUNCATE {MYSQL_DATABASE}.users;"
    cursor.execute(query)
    conn.commit()
    conn.close()
