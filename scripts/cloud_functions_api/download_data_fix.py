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

    # Extract passed user data
    user_id = request_json.get('user_id')

    # Get valid business data by that particular user
    query = (
        f"""
        SELECT
            data_id,
            data_value,
            data_details,
            CAST(created_at AS CHAR) AS created_at,
            CAST(modified_at AS CHAR) AS last_modified
        FROM secured.business_data_fix
        WHERE user_id = '{user_id}' AND is_valid = 1;
        """
    )

    cursor.execute(query)
    view_data_result = cursor.fetchall()

    activity = 'Data is downloaded'
    query = (
        f"""
        INSERT INTO secured.user_activity_log_fix (user_id, data_id, activity)
        VALUES ({user_id}, 0, '{activity}');
        """
    )
    print(query)
    cursor.execute(query)
    conn.commit()


    conn.close()

    return {
        'code': 200,
        'message': 'Business data fetched',
        'data':view_data_result
    }
