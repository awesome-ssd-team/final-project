# pylint: disable=invalid-name
# pylint: disable=duplicate-code
'''The Cloud Functions module for handling verifying OTP'''
import os
import mysql.connector

def main(request):
    '''The main function of handling the verifying OTP request'''
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
    user_id = request_json.get('user_id')

    query = (
        f"""
        SELECT tfa_secret FROM {SECURED_DATABASE}.users
        WHERE user_id = {user_id}
        """
    )

    cursor.execute(query)
    result = cursor.fetchone()
    tfa_secret = result.get('tfa_secret') if result else None
    conn.close()

    if tfa_secret:
        return {
            'code': 200,
            'message': 'OTP secrest is saved.',
            'data': {
                'tfa_secret': tfa_secret
            }
        }
    return {
        'code': 406,
        'message': 'TFA secret not found.'
    }
