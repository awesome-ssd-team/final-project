# pylint: disable=no-self-use
'''The unit test cases for the verify OTP module'''
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import verify_otp

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('turncate_users')
class TestVerifyOTP:
    '''The unit test cases group'''

    def test_when_tfa_secret_is_saved(self):
        '''Test when the TFA secret is saved in the database'''
        data = {
            'user_id': '1',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = verify_otp.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert response['data']['tfa_secret'] is not None

    def test_setup_otp_with_non_existing_user(self):
        '''Test when the TFA secret is not existed in the database'''
        data = {
            'user_id': '999999',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = verify_otp.main(request)
        assert response is not None
        assert response['code'] == 406
