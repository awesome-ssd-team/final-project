import os
import mysql.connector
import uuid


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
    activity = None

    # Extract passed user data
    user_id = request_json.get('user_id')
    data_value = request_json.get('data_value')
    data_details = request_json.get('data_details')


    # Generate token & insert into table as an acknowledge token
    auth_token = str(uuid.uuid4())

    query = (
        f"""
        INSERT INTO secured.business_data_fix (user_id, data_value, data_details, is_valid)
        VALUES ({user_id},{data_value},'test{data_details}',1);
        """
    )

    print(query)
    cursor.execute(query)
    conn.commit()

    activity = f'Data is added'

    query = (
        f"""
        INSERT INTO secured.user_activity_log_fix (user_id, data_id, activity)
        VALUES ({user_id}, (select max(data_id) from secured.business_data_fix), '{activity}');
        """
    )
    print(query)
    cursor.execute(query)
    conn.commit()

    conn.close()

    return {
        'code': 200,
        'message': f'{activity}',
        'data': {
            "user_id": user_id,
        }
    }

