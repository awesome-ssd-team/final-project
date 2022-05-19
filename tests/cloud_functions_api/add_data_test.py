# pylint: disable=no-self-use
'''The unit test cases for the adding business data module'''
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import add_data

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('truncate_backend_users')
@pytest.mark.usefixtures('truncate_backend_user_login_logs')
@pytest.mark.usefixtures('truncate_backend_blocked_sessions')
@pytest.mark.usefixtures('truncate_users')
class TestAddData:
    '''The unit test cases group'''

    def test_add_data(self):
        '''
        Test the main function of handling adding data to the database
        '''
        data = {
            'user_id': '1',
            'data_value': 3,
            'data_details': 'This is sample data',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = add_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200

    def test_add_data_with_non_existing_user(self):
        '''
        Test the main function of handling adding data for an non existing user
        '''
        data = {
            'user_id': '2',
            'data_value': 4,
            'data_details': 'This is sample data',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = add_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
