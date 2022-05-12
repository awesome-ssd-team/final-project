# pylint: disable=no-self-use
'''The unit test cases for the setup OTP module'''
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import setup_otp

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('turncate_users')
class TestSetupOTP:
    '''The unit test cases group'''

    def test_setup_otp(self, fake_user_data):
        '''Test setup the OTP for the user'''
        user_data = fake_user_data
        assert isinstance(user_data, dict)

        data = {
            'otp_secret': '654321',
            'user_email': user_data['email'],
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = setup_otp.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200

    def test_setup_otp_with_non_existing_user(self):
        '''Test setup the TOP for an non existing user'''
        data = {
            'otp_secret': '654321',
            'user_email': 'johndoe@gmail.com',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = setup_otp.main(request)
        assert response is not None
        assert response['code'] == 200
