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
    #cursor = conn.cursor(OrderedDictCursor)

    # Extract passed user data
    user_id = request_json.get('user_id')

    # Get valid business data by that particular user
    query = (
        f"""
        SELECT
            user_id,
            data_id,
            activity,
            activity_id,
            created_at as created_at
        FROM secured.user_activity_log_fix;
        """
    )

    cursor.execute(query)
    view_data_result = cursor.fetchall()

    conn.close()

    return {
        'code': 200,
        'message': 'Log is view by admin {user_id}',
        'data':view_data_result
    }
