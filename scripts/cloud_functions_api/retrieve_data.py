# pylint: disable=invalid-name
# pylint: disable=duplicate-code
# pylint: disable=too-many-locals
'''The Cloud Functions module for handling retrieving data'''
import os
import mysql.connector

def main(request):
    '''The main function of handling the retrieving data request'''
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
        database='secured'
    )

    cursor = conn.cursor(dictionary=True)

    # Extract passed user data
    user_id = request_json.get('user_id')

    # Get valid business data by that particular user
    query = (
        f"""
        SELECT
            data_id,
            data_value,
            data_details,
            last_modified,
            is_valid
        FROM {SECURED_DATABASE}.business_data
        WHERE user_id = '{user_id}' AND is_valid = 1;
        """
    )

    cursor.execute(query)
    view_data_result = cursor.fetchall()

    conn.close()

    return {
        'code': 200,
        'message': 'Business data fetched',
        'data': view_data_result
    }
