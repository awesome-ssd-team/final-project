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
    data_id = uuid.uuid4()
    is_valid = 1
    last_modified = str(datetime.datetime.now())[:-7]


    # Add data to database
    query = (
        f"""
        INSERT INTO secured.business_data (data_id, user_id, data_value, data_details, is_valid, last_modified)
        VALUES ('{data_id}',{user_id},{data_value},'{data_details}',{is_valid},'{last_modified}');
        """
    )
    print("DEBUG",query)
    cursor.execute(query)
    conn.commit()
    conn.close()

    return {
        'code': 200,
        'message': f'Data (id:{data_id}) is added',
    }
