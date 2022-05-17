import os
import mysql.connector
import uuid
import datetime

def main(request):
    request_json = request.get_json()

    # Connect to MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database='secured'
    )

    cursor = conn.cursor(dictionary=True)

    # Extract passed user data
    user_id = request_json.get('user_id')
    data_value = request_json.get('data_value')
    data_details = request_json.get('data_details')
    is_valid = 1


    # Add data to database
    query = (
        f"""
        INSERT INTO secured.business_data_fix (user_id, data_value, data_details, is_valid)
        VALUES ({user_id},{data_value},'{data_details}', {is_valid});
        """
    )

    print(query)

    cursor.execute(query)
    conn.commit()
    conn.close()

    return {
        'code': 200,
        'message': f'Data is added.',
    }
