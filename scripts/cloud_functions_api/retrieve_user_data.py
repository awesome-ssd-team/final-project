import os
import mysql.connector
import uuid

def main(request):
    request_json = request.get_json()

    # Get All
    user_id = request_json.get('user_id')

    # Connect to MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database='backend'
    )

    cursor = conn.cursor(dictionary=True)

    # Get valid business data by that particular user
    if not user_id:
        query = (
            f"""
            SELECT
                user_id,
                CAST(created_at AS CHAR) AS created_at,
                CAST(updated_at AS CHAR) AS updated_at,
                CAST(full_name AS CHAR CHARACTER SET utf8) AS full_name,
                CAST(email AS CHAR CHARACTER SET utf8) AS email,
                is_tfa_enabled,
                CAST(is_active AS UNSIGNED) AS is_active,
                CAST(is_admin AS UNSIGNED) AS is_admin
            FROM backend.users
            ORDER BY created_at DESC;
            """
        )
    else:
        query = (
            f"""
                SELECT
                    user_id,
                    CAST(created_at AS CHAR) AS created_at,
                    CAST(updated_at AS CHAR) AS updated_at,
                    CAST(full_name AS CHAR CHARACTER SET utf8) AS full_name,
                    CAST(email AS CHAR CHARACTER SET utf8) AS email,
                    is_tfa_enabled,
                    CAST(is_active AS UNSIGNED) AS is_active,
                    CAST(is_admin AS UNSIGNED) AS is_admin
                FROM backend.users
                WHERE user_id = {user_id};
            """
        )

    cursor.execute(query)
    view_data_result = cursor.fetchall()
    print(view_data_result)

    conn.close()

    return {
        'code': 200,
        'message': 'User data fetched',
        'data': view_data_result
    }
