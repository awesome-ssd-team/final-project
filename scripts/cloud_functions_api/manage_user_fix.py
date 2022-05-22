# pylint: disable=invalid-name
# pylint: disable=duplicate-code
'''The Cloud Functions module for handling user registration'''
import os
import mysql.connector


def main(request):
    '''The main function of handling the user registration request'''
    request_json = request.get_json()
    admin_id = request_json.get('admin_id')
    user_id = request_json.get('user_id')
    column = request_json.get('column')
    value = request_json.get('value')

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

    query = (
        f"""
        UPDATE {SECURED_DATABASE}.users
        SET
            {column} = {value}
        WHERE
            user_id = {user_id}
        """
    )

    cursor.execute(query)
    conn.commit()

    # Log the activity
    try:
        log_query = (
            f"""
            INSERT INTO secured.user_activity_log_fix (user_id, data_id, activity)
            VALUES ({admin_id}, {user_id}, 'Change column {column} of user_id {user_id} to {value}')
            """
        )

        cursor.execute(log_query)
        conn.commit()
        conn.close()
    except:
        pass

    return {
        'code': 200,
        'message': f"User data {user_id} column {column} has been updated!"
    }
