# pylint: disable=no-self-use
'''The unit test cases for the updating business data module'''
from unittest.mock import Mock
import pytest

from scripts.cloud_functions_api import update_data

@pytest.mark.usefixtures('create_a_testing_user_account')
@pytest.mark.usefixtures('create_a_business_data_record')
@pytest.mark.usefixtures('truncate_backend_users')
@pytest.mark.usefixtures('truncate_backend_user_login_logs')
@pytest.mark.usefixtures('truncate_backend_blocked_sessions')
@pytest.mark.usefixtures('truncate_users')
class TestUpdateData:
    '''The unit test cases group'''

    def test_update_data_with_unsupported_action(self):
        '''
        Test the main function of handling the request with an unsupported action
        '''
        data = {
            'update_action': '99999',
        }
        request = Mock(get_json=Mock(return_value=data), args=data)
        response = update_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 400

    def test_updating_the_data_value(self, fake_business_data):
        '''
        Test the main function of handling the updating data value request
        '''
        data = fake_business_data
        payload = {
            'user_id': data['user_id'],
            'data_id': data['data_id'],
            'update_action': '1',
            'data_value': 5,
            'data_details': 'This is sample data',
        }
        request = Mock(get_json=Mock(return_value=payload), args=payload)
        response = update_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert response['data']['user_id'] is not None
        assert response['data']['user_id'] == data['user_id']

    def test_updating_the_data_details(self, fake_business_data):
        '''
        Test the main function of handling the updating data details request
        '''
        data = fake_business_data
        payload = {
            'user_id': data['user_id'],
            'data_id': data['data_id'],
            'update_action': '2',
            'data_value': 5,
            'data_details': 'This is sample data 2',
        }
        request = Mock(get_json=Mock(return_value=payload), args=payload)
        response = update_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert response['data']['user_id'] is not None
        assert response['data']['user_id'] == data['user_id']

    def test_marking_delete(self, fake_business_data):
        '''
        Test the main function of handling the marking delete business data request
        '''
        data = fake_business_data
        payload = {
            'user_id': data['user_id'],
            'data_id': data['data_id'],
            'update_action': '3',
        }
        request = Mock(get_json=Mock(return_value=payload), args=payload)
        response = update_data.main(request)
        assert response is not None
        assert isinstance(response, dict)
        assert response['code'] == 200
        assert response['data'] is not None
        assert response['data']['user_id'] is not None
        assert response['data']['user_id'] == data['user_id']
