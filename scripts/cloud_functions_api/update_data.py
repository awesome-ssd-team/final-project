import os
import mysql.connector
import uuid

def main(request):
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
    data_id = request_json.get('data_id')
    update_action = request_json.get('update_action')
    data_value = request_json.get('data_value')
    data_details = request_json.get('data_details')

    # THIS IS A UPDATE ACTION THAT UPDATE AN ENTRY'S DATA VALUE
    if update_action == '1':
        # Generate token & insert into table as an acknowledge token
        auth_token = str(uuid.uuid4())

        query = (
            f"""
            UPDATE {SECURED_DATABASE}.business_data
            SET data_value = {data_value},
                last_modified = CURRENT_TIMESTAMP()
            WHERE user_id = {user_id} AND data_id = '{data_id}';
            """
        )

        cursor.execute(query)
        conn.commit()


        return {
            'code': 200,
            'message': f'Data id {data_id} is updated by user {user_id} - data value: {data_value}!',
            'data': {
                "user_id": user_id,
            }
        }

    # THIS IS A UPDATE ACTION THAT UPDATE AN ENTRY'S DATA DETAILS
    elif update_action == '2':
        # Add attempt to user_login_logs
        query = (
            f"""
            UPDATE {SECURED_DATABASE}.business_data
            SET data_details = '{data_details}',
                last_modified = CURRENT_TIMESTAMP()
            WHERE user_id = {user_id} AND data_id = '{data_id}'
            """
        )
        cursor.execute(query)
        conn.commit()
        # activity_2 = f'data_details is updated to {data_details}'

        return {
            'code': 200,
            'message': f'Data id {data_id} is updated by user {user_id} - data details: {data_details}!',
            'data': {
                "user_id": user_id,
            }
        }


    # THIS IS A UPDATE ACTION THAT DELETES AN ENTRY - BUT IN DB IT SIMPLY PUTS THE is_active = 0, THUS TECHNICALLY AN UPDATE...
    elif update_action == '3':

        query = (
            f"""
            UPDATE {SECURED_DATABASE}.business_data
            SET is_valid = '0',
                last_modified = CURRENT_TIMESTAMP()
            WHERE user_id = {user_id} AND data_id = '{data_id}'
            """
        )
        cursor.execute(query)
        conn.commit()
        conn.close()

        return {
            'code': 200,
            'message': f'Data id {data_id} is deleted by user {user_id}!',
            'data': {
                "user_id": user_id,
            }
        }

    return {
        'code': 400,
        'message': 'Unsupported action',
    }
