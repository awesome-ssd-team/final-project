# pylint: disable=no-self-use
# pylint: disable=invalid-name
'''The system integration test cases for Google Cloud Functions API'''
import json
import pytest
import requests

@pytest.mark.usefixtures('turncate_backend_users')
@pytest.mark.usefixtures('turncate_users')
class TestGoogleCloudFunctions:
    '''The system integration test cases group'''

    def test_google_cloud_functions_heart_beat(self):
        ''''
        Test whether Google Cloud Functions has heart beat or not
        '''
        http_response = requests.get(
            'https://us-central1-ssd-136542.cloudfunctions.net/heart-beat'
        )
        response = http_response.text

        assert response is not None
        assert str(response) == 'It is alive!'

    def test_google_cloud_functions_register_user(self, fake_user_data):
        '''
        Test wether Google Cloud Functions can handle the user registration request or not
        '''
        data = fake_user_data

        http_payload = {
            "full_name": data['full_name'],
            "email": data['email'],
            "password": data['password'],
            "secondary_password": data['secondary_password']
        }

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/test_register_user',
            headers={"Content-Type": "application/json"},
            data=json.dumps(http_payload)
        )

        response = json.loads(http_response.content)
        status_code = response.get('code')
        message = response.get('message')

        assert status_code == 200
        assert message is not None
        assert message != ''