# pylint: disable=invalid-name
# pylint: disable=too-many-locals
'''The Cloud Functions module for handling user authentication'''
import os
import uuid
import mysql.connector

def main(request):
    '''The main function of handling the user authentication request'''
    request_json = request.get_json()

    # Connect to MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SECURED_DATABASE = os.environ.get('SECURED_DATABASE')
    BACKEND_DATABASE = os.environ.get('BACKEND_DATABASE')

    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        database=SECURED_DATABASE,
    )

    cursor = conn.cursor(dictionary=True)

    # Extract passed user data
    email = request_json.get('email')
    password = request_json.get('password')
    session_id = request_json.get('session_id')

    code = 0
    message = None
    data = None

    # Get entered user_id & name (if any)
    query = (
        f"""
        SELECT
            user_id,
            SUBSTRING_INDEX(full_name, ' ', 1) AS user_name,
            is_tfa_enabled,
            is_admin
        FROM {SECURED_DATABASE}.users
        WHERE email = '{email}'
        AND is_active = TRUE;
        """
    )

    cursor.execute(query)
    user_id_result = cursor.fetchone()

    if user_id_result is None:
        # No record matches with user inputted email
        code = 406
        message = 'No record matches.'

    user_id = user_id_result.get('user_id') if user_id_result else None
    user_name = user_id_result.get('user_name') if user_id_result else None
    is_tfa_enabled = bool(user_id_result.get('is_tfa_enabled')) if user_id_result else None
    is_admin = bool(user_id_result.get('is_admin')) if user_id_result else None
    user_id_value = user_id if user_id is not None else 'NULL'

    # Add attempt to user_login_logs
    query = (
        f"""
            INSERT INTO {BACKEND_DATABASE}.user_login_logs
                (user_id, session_id)
            VALUES
                ({user_id_value}, '{session_id}');
            """
    )
    cursor.execute(query)
    conn.commit()

    # Check if credentials is blocked
    query = (
        f"""
            SELECT TRUE AS is_blocked
            FROM {BACKEND_DATABASE}.blocked_session
                WHERE (
                    session_id = '{session_id}' OR user_id = {user_id_value}
                )
                AND ( CURRENT_TIMESTAMP() BETWEEN blocked_at AND blocked_until );
        """
    )

    cursor.execute(query)
    is_blocked_result = cursor.fetchone()
    is_blocked = is_blocked_result.get('is_blocked') if is_blocked_result else False

    # Check if user_id is blocked due to malicious login attempt
    if is_blocked:
        code = 403
        message = ("You or the credentials you are using is currently being blocked. "
                        "Please try again later.")

        # return {
        #     'code': 403,
        #     'message': ("You or the credentials you are using is currently being blocked. "
        #                 "Please try again later.")
        # }

    # Check if credentials are correct
    if code == 0:
        query = (
            f"""
                SELECT (MD5('{password}') = A.password) AS authenticated
                FROM {BACKEND_DATABASE}.users A
                    LEFT JOIN {SECURED_DATABASE}.users B
                    ON A.user_id = B.user_id
                WHERE A.email = AES_ENCRYPT('{email}', B.secondary_password);
            """
        )

        cursor.execute(query)
        query_result = cursor.fetchone()
        authenticated = bool(query_result.get('authenticated')) if query_result else False

        if authenticated:
            # Generate token & insert into table as an acknowledge token
            auth_token = str(uuid.uuid4())

            query = (
                f"""
                INSERT INTO {SECURED_DATABASE}.user_login_token (auth_token, user_id, expired_at)
                VALUES (
                    '{auth_token}', {user_id}, CURRENT_TIMESTAMP() + INTERVAL 15 MINUTE
                );
                """
            )

            cursor.execute(query)
            conn.commit()

            code = 200
            message = f'Welcome {user_name}!'
            data = {
                "auth_token": auth_token,
                "user_id": user_id,
                "user_name": user_name,
                "is_tfa_enabled": is_tfa_enabled,
                "is_admin": is_admin
            }
        else:
            code = 404
            message = "Credentials are not recognized..."

    # Check if attempt by device >= 3. Add to block if yes.
    query = (
        f"""
        SELECT
            (COUNT(*) > 3) AS more_than_three
        FROM
            {BACKEND_DATABASE}.user_login_logs
        WHERE
            session_id = '{session_id}';
        """
    )

    cursor.execute(query)
    attempt_result = cursor.fetchone()
    attempt_made = attempt_result.get('more_than_three') if attempt_result else 0

    print(f'attempt_made: {attempt_made}')

    if int(attempt_made) == 1:
        query = (
            f"""
            INSERT INTO {BACKEND_DATABASE}.blocked_session
                (session_id, user_id, blocked_at, blocked_until)
            SELECT
                session_id,
                user_id,
                CURRENT_TIMESTAMP(),
                CURRENT_TIMESTAMP() + INTERVAL 15 MINUTE
            FROM
                {BACKEND_DATABASE}.user_login_logs
            WHERE
                session_id = '{session_id}' AND user_id IS NOT NULL
            GROUP BY
                1,2;
            """
        )

        cursor.execute(query)
        conn.commit()

        code = 401
        message = 'Maximum attempt, you get temporary ban.'

    conn.close()

    return {
        'code': code,
        'message': message,
        'data': data
    }
