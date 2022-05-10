'''The unit test cases for the register user module'''
# pylint: disable=no-self-use
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import register_user

@pytest.mark.usefixtures("turncate_users")
class TestRegisterUser:
    '''The unit test cases group'''

    def test_main_with_non_registered_email_address(self, fake_user_data):
        '''
        Test the main function of handling the user registration request
        for non registered email address
        '''
        data = fake_user_data
        assert isinstance(data, dict)
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = register_user.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['message'] == 'Registration success! You can now login.'

    def test_main_with_an_registered_email_address(self, fake_user_data):
        '''
        Test the main function of handling the user registration request
        for registered email address
        '''
        data = fake_user_data
        assert isinstance(data, dict)
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = register_user.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 406
        assert response['message'] == 'Email is already registered.'
