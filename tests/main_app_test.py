# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda
'''The end to end test cases for the main application'''
import os
import re
import pytest

from scripts import MainApp

@pytest.mark.usefixtures('turncate_backend_users')
@pytest.mark.usefixtures('turncate_backend_user_login_logs')
@pytest.mark.usefixtures('turncate_backend_blocked_sessions')
@pytest.mark.usefixtures('turncate_users')
class TestMainApplication:
    '''The end to end test cases group'''

    def _fetch_steps_from_file(self, steps_filename, input_values):
        '''Fetch the steps from specified file'''
        with open(f'{os.getcwd()}/tests/steps/{steps_filename}', 'r', encoding='utf-8') as steps:
            for step in steps.readlines():
                input_values.append(re.sub('\n', '', step))

    def _mock_input(self, s, input_values, output, sequences=None):
        '''Mock user\'s input'''

        def _append_sequences(inp, oup):
            if sequences is not None:
                sequences.append({
                    'output': inp,
                    'input': oup,
                })

        output.append(s)

        if s.startswith('Enter your MFA code'):
            input_values.pop(0)

            for code in output:
                if code.startswith('OTP:'):
                    mfa_code = re.sub('OTP:', '', code)
                    _append_sequences(s, mfa_code)
                    output.remove(code)
                    return mfa_code

        _append_sequences(s, input_values[0])

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

    def test_user_login(self):
        '''
        Test the scenario of user authentication flow
        '''
        input_values = []
        output = []
        sequences = []

        self._fetch_steps_from_file('user_login.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output, sequences)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output, sequences)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome jd!',
            'Enter your MFA code: ',
            'Hi jd! You are logged in! Press any key to continue...',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            '=========================================================================================================================================================',
            'What action you would like to take?',
            '========================================',
            '',
            '1. Add Data',
            '2. Update Data',
            '3. Delete Data ',
            '4. Download Data\n',
            '5. Logout\n',
            'Please select a menu: ',
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
        ]
