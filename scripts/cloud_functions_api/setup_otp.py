# pylint: disable=invalid-name
# pylint: disable=duplicate-code
'''The Cloud Functions module for handling setting up OTP'''
import os
import mysql.connector

def main(request):
    '''The main function of handling the setup OTP request'''
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
    otp_secret = request_json.get('otp_secret')
    user_email = request_json.get('email')

    query = (
        f"""
        UPDATE {SECURED_DATABASE}.users
        SET
            tfa_secret = '{otp_secret}',
            is_tfa_enabled = TRUE
        WHERE
            email = '{user_email}';
        """
    )

    cursor.execute(query)
    conn.commit()
    conn.close()

    return {
        'code': 200,
        'message': 'OTP secrest is saved.'
    }
