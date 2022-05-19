# pylint: disable=no-self-use
'''The unit test cases for the retrieving business data module'''
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import retrieve_data

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('create_a_business_data_record')
@pytest.mark.usefixtures('truncate_backend_users')
@pytest.mark.usefixtures('truncate_backend_user_login_logs')
@pytest.mark.usefixtures('truncate_backend_blocked_sessions')
@pytest.mark.usefixtures('truncate_business_data')
@pytest.mark.usefixtures('truncate_users')
class TestRetrieveData:
    '''The unit test cases group'''

    def test_retrieve_data(self):
        '''
        Test the main function of handling retrieving data to the database
        '''
        payload = {'user_id': '1'}
        request = Mock(get_json=Mock(return_value=payload), args=payload)
        response = retrieve_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert len(response['data']) > 0

    def test_retrieve_data_with_non_existing_user(self):
        '''
        Test the main function of handling retrieving data for an non existing user
        '''
        payload = {'user_id': '2'}
        request = Mock(get_json=Mock(return_value=payload), args=payload)
        response = retrieve_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert len(response['data']) == 0
