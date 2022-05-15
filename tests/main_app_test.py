# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda
'''The end to end test cases for the main application'''
import os
import re
import pytest

from scripts import MainApp

@pytest.mark.usefixtures('turncate_backend_users')
@pytest.mark.usefixtures('turncate_users')
class TestMainApplication:
    '''The end to end test cases group'''

    def _fetch_steps_from_file(self, steps_filename, input_values):
        '''Fetch the steps from specified file'''
        with open(f'{os.getcwd()}/tests/steps/{steps_filename}', 'r', encoding='utf-8') as steps:
            for step in steps.readlines():
                input_values.append(re.sub('\n', '', step))
            # steps.close()

    def _mock_input(self, s, input_values, output):
        '''Mock user\'s input'''
        output.append(s)
        return input_values.pop(0)

    def test_register_user(self):
        '''
        Test the scenario of user registration flow
        '''
        input_values = []
        output = []

        self._fetch_steps_from_file('register_user.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        assert output == [
            'Welcome!\n',
            '1. Login', '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Your full name: ',
            'Your email: ',
            'Enter your password: ',
            'Confirm your password: ',
            'Set a secondary password: ',
            'Confirm your secondary password: ',
            {
                'full_name':
                'John Doe',
                'email': 'johndoe@gmail.com',
                'password':
                'P@ssw0rd',
                'secondary_password': '123456'
            },
            '{"code":200,"message":"Registration success! You can now login."}\n',
            'Registration success! You can now login.',
            'We suggest you to setup Two Factor Authorization (TFA) to secure your account.',
            'Do you want to set it up now? (y/n): ',
            'Welcome!\n', '1. Login', '2. Register\n', '0. Exit\n',
            'Please select a menu: '
        ]
