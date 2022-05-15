# pylint: disable=no-self-use
# pylint: disable=invalid-name
'''The system integration test cases for Amazon RDS'''
import os
import pytest
import mysql.connector

@pytest.mark.usefixtures('turncate_backend_users')
@pytest.mark.usefixtures('turncate_users')
class TestAmazonRDS:
    '''The system integration test cases group'''

    def test_can_make_connection_to_amazon_rds(self):
        '''
        Test the connection between Amazon RDS
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
            )
            assert conn is not None

            query = 'SHOW DATABASES;'
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result_set = cursor.fetchall()
            assert len(result_set) != 0

            conn.close()

        except Exception as e:
            raise AssertionError from e

    def test_required_databases_are_exist(self):
        '''
        Test whether all required databases are exist or not
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
        SECURED_DATABASE = os.environ.get('SECURED_DATABASE')
        BACKEND_DATABASE = os.environ.get('BACKEND_DATABASE')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
            )
            assert conn is not None
            query = 'SHOW DATABASES;'
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result_set = cursor.fetchall()
            assert len(result_set) != 0

            has_found_secured_database = False
            has_found_backend_database = False

            for database in result_set:
                if database['Database'] == SECURED_DATABASE:
                    has_found_secured_database = True
                elif database['Database'] == BACKEND_DATABASE:
                    has_found_backend_database = True

            assert has_found_secured_database is True
            assert has_found_backend_database is True

            conn.close()

        except Exception as e:
            raise AssertionError from e

    def test_can_perform_read_operations(self):
        '''
        Test whether the application can perform read operations or not
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
        SECURED_DATABASE = os.environ.get('SECURED_DATABASE')
        BACKEND_DATABASE = os.environ.get('BACKEND_DATABASE')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=SECURED_DATABASE,
            )
            assert conn is not None
            query = f'SELECT * FROM {SECURED_DATABASE}.users LIMIT 1;'
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result_set = cursor.fetchall()
            assert result_set is not None
            conn.close()

            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=BACKEND_DATABASE,
            )
            assert conn is not None
            query = f'SELECT * FROM {BACKEND_DATABASE}.users LIMIT 1;'
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result_set = cursor.fetchall()
            assert result_set is not None
            conn.close()

        except Exception as e:
            raise AssertionError from e

    def test_can_perform_insert_operations(self, fake_user_data):
        '''
        Test whether the application can perform insert operations or not
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
        SECURED_DATABASE = os.environ.get('SECURED_DATABASE')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=SECURED_DATABASE,
            )
            assert conn is not None
            fake_user = fake_user_data
            assert isinstance(fake_user, dict)

            query = (
                f"""
                INSERT INTO {SECURED_DATABASE}.users
                    (password, full_name, email, secondary_password, tfa_secret)
                VALUES
                    (
                        '{fake_user['password']}',
                        '{fake_user['full_name']}',
                        '{fake_user['email']}',
                        '{fake_user['secondary_password']}',
                        '654321'
                    );
                """
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            conn.commit()

            query = f"SELECT * FROM {SECURED_DATABASE}.users WHERE email = '{fake_user['email']}';"
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            result_set = cursor.fetchone()

            assert result_set is not None
            assert result_set['full_name'] == fake_user['full_name']

            conn.close()

        except Exception as e:
            raise AssertionError from e

    def test_can_perform_update_operations(self, fake_user_data):
        '''
        Test whether the application can perform update operations or not
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
        SECURED_DATABASE = os.environ.get('SECURED_DATABASE')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=SECURED_DATABASE,
            )
            assert conn is not None

            fake_user = fake_user_data
            assert isinstance(fake_user, dict)
            email = fake_user['email']
            cursor = conn.cursor(dictionary=True)

            query = f"""
                SELECT * FROM {SECURED_DATABASE}.users
                WHERE email = '{email}';
                """
            cursor.execute(query)
            result_set = cursor.fetchone()
            assert result_set is not None

            full_name = 'John Doe'

            query = (
                f"""
                UPDATE {SECURED_DATABASE}.users
                SET
                    full_name = '{full_name}'
                WHERE
                    user_id = '{result_set['user_id']}';
                """
            )
            cursor.execute(query)
            conn.commit()

            query = f"""
                    SELECT * FROM {SECURED_DATABASE}.users
                    WHERE user_id = '{result_set['user_id']}';
                    """
            cursor.execute(query)
            result_set = cursor.fetchone()

            assert result_set is not None
            assert result_set['full_name'] == full_name

            conn.close()

        except Exception as e:
            raise AssertionError from e

    def test_can_perform_delete_operations(self, fake_user_data):
        '''
        Test whether the application can perform delete operations or not
        '''
        MYSQL_HOST = os.environ.get('MYSQL_HOST')
        MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
        SECURED_DATABASE = os.environ.get('SECURED_DATABASE')

        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USERNAME,
                password=MYSQL_PASSWORD,
                database=SECURED_DATABASE,
            )
            assert conn is not None

            fake_user = fake_user_data
            assert isinstance(fake_user, dict)
            email = fake_user['email']
            cursor = conn.cursor(dictionary=True)

            query = f"""
                SELECT * FROM {SECURED_DATABASE}.users
                WHERE email = '{email}';
            """
            cursor.execute(query)
            result_set = cursor.fetchone()
            assert result_set is not None

            query = f"""
                DELETE FROM {SECURED_DATABASE}.users
                WHERE user_id = '{result_set['user_id']}';
            """
            cursor.execute(query)
            conn.commit()
            conn.close()

        except Exception as e:
            raise AssertionError from e
