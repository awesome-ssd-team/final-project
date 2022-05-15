# pylint: disable=invalid-name
# pylint: disable=duplicate-code
'''The Cloud Functions module for handling user registration'''
import os
import mysql.connector

def main(request):
    '''The main function of handling the user registration request'''
    request_json = request.get_json()

    # Connect to MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SECURED_DATABASE = os.environ.get('SECURED_DATABASE')

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database=SECURED_DATABASE,
    )

    cursor = conn.cursor(dictionary=True)

    # Extract passed user data
    full_name = request_json.get('full_name')
    email = request_json.get('email')
    password = request_json.get('password')
    secondary_password = request_json.get('secondary_password')

    # Check if email is already registered
    query = f"SELECT True AS available FROM {SECURED_DATABASE}.users WHERE email = '{email}';"
    cursor.execute(query)
    query_result = cursor.fetchone()

    if query_result:
        # Reject registration data
        return {
            'code': 406,
            'message': "Email is already registered."
        }

    # Create new users
    query = (
        f"""
        INSERT INTO {SECURED_DATABASE}.users (password, full_name, email, secondary_password)
        VALUES ('{password}', '{full_name}', '{email}', '{secondary_password}');
        """
    )
    cursor.execute(query)
    conn.commit()
    conn.close()

    return {
        'code': 200,
        'message': "Registration success! You can now login."
    }
