# pylint: disable=no-self-use
'''The unit test cases for the user login module'''
from unittest.mock import Mock
import uuid
import pytest

from scripts.cloud_functions_api import user_login

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('turncate_backend_users')
@pytest.mark.usefixtures('turncate_users')
class TestUserLogin:
    '''The unit test cases group'''

    def test_user_login_with_valid_credentials(self, fake_user_data):
        '''Test when user has inputted valid credentials'''
        user_data = fake_user_data
        assert isinstance(user_data, dict)

        data = {
            'email': user_data['email'],
            'password': user_data['password'],
            'session_id': str(uuid.uuid4()),
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = user_login.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert isinstance(response['data'], dict)
        assert response['data']['auth_token'] is not None

    def test_user_login_with_invalid_email_address(self, fake_user_data):
        '''Test when user has inputted invalid email address'''
        user_data = fake_user_data
        assert isinstance(user_data, dict)

        data = {
            'email': 'johndoe@gmail.com',
            'password': user_data['password'],
            'session_id': str(uuid.uuid4()),
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = user_login.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 406

    def test_user_has_exceeded_login_attempt(self, fake_user_data):
        '''
        Test when user has exceed the login attempt limit.
        The server will block the user trying to login after allowed attempts are exceeded.
        '''
        user_data = fake_user_data
        assert isinstance(user_data, dict)

        data = {
            'email': user_data['email'],
            'password': 'invalid_password',
            'session_id': str(uuid.uuid4()),
        }

        login_attempt = 0

        while login_attempt < 3:
            print(f'Trying to login with {login_attempt + 1} attempt.')

            request = Mock(get_json=Mock(return_value=data), args=data)
            response = user_login.main(request)
            assert response is not None
            assert isinstance(response, dict)
            assert response['code'] == 406
            login_attempt += 1

        request = Mock(get_json=Mock(return_value=data), args=data)
        response = user_login.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 401
        assert response['message'] == (
            'You or the credentials you are using is currently being blocked. '
            'Please try again later.'
        )
