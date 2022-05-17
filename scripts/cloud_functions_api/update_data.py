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
    data_id = request_json.get('data_id')
    update_action = request_json.get('update_action')
    data_value = request_json.get('data_value')
    data_details = request_json.get('data_details')

    if update_action == '1':
        # Generate token & insert into table as an acknowledge token
        auth_token = str(uuid.uuid4())

        query = (
            f"""
            UPDATE secured.business_data_fix
            SET data_value = {data_value}
            WHERE user_id = {user_id} AND data_id = '{data_id}';
            """
        )

        print(query)
        cursor.execute(query)
        conn.commit()

        activity = f'data_value is updated to {data_value}'

    elif update_action == '2':
        # Add attempt to user_login_logs
        query = (
            f"""
            UPDATE secured.business_data_fix
            SET data_details = '{data_details}'
            WHERE user_id = {user_id} AND data_id = '{data_id}'
            """
        )
        print(query)
        cursor.execute(query)
        conn.commit()

        activity = f'data_details is updated to {data_details}'

    # THIS IS A UPDATE ACTION THAT DELETES AN ENTRY - BUT IN DB IT SIMPLY PUTS THE is_active = 0, THUS TECHNICALLY AN UPDATE...
    elif update_action == '3':

        query = (
            f"""
            UPDATE secured.business_data_fix
            SET is_valid = 0
            WHERE user_id = {user_id} AND data_id = '{data_id}'
            """
        )
        print(query)
        cursor.execute(query)
        conn.commit()
        activity = 'Data is deleted'

    query = (
        f"""
        INSERT INTO secured.user_activity_log_fix (user_id, data_id, activity)
        VALUES ({user_id}, {data_id}, '{activity}');
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

