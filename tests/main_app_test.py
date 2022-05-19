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
@pytest.mark.usefixtures('turncate_business_data')
@pytest.mark.usefixtures('turncate_users')
class TestMainApplication:
    UUID_PATTERN = r'[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}'
    DATETIME_PATTENT = r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (\d{2}) (Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT'

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

        print(f'Asking for input: {s}')
        print(f'Current input values: {input_values}')

        output.append(s)

        if s.startswith('Enter your MFA code') or s.startswith('Enter the code'):
            input_values.pop(0)

            for code in output:
                if code.startswith('OTP:'):
                    mfa_code = re.sub('OTP:', '', code)
                    _append_sequences(s, mfa_code)
                    output.remove(code)
                    return mfa_code

        _append_sequences(s, input_values[0])

        return input_values.pop(0)

    def _extract_uuid(self, s):
        match_uuid_regex = re.compile(TestMainApplication.UUID_PATTERN)
        result = match_uuid_regex.findall(s)
        return result[0] if len(result) > 0 else None

    def _replace_uuid(self, replace_with, s):
        result = re.sub(
            TestMainApplication.UUID_PATTERN,
            replace_with,
            s,
        )
        return str(result)

    def _extract_datetime(self, s, first_result=True):
        match_uuid_regex = re.compile(TestMainApplication.DATETIME_PATTENT)
        result = match_uuid_regex.findall(s)
        if len(result) > 0:
            idx = 0 if first_result else len(result) - 1
            return '{}, {} {} {} {}:{}:{} GMT'.format(
                result[idx][0],
                result[idx][1],
                result[idx][2],
                result[idx][3],
                result[idx][4],
                result[idx][5],
                result[idx][6],
            )
        return None

    def _replace_datetime(self, replace_with, s):
        result = re.sub(
            TestMainApplication.DATETIME_PATTENT,
            replace_with,
            s,
        )
        return str(result)

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
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Your full name: ',
            'Your email: ',
            'Enter your password: ',
            'Confirm your password: ',
            'Set a secondary password: ',
            'Confirm your secondary password: ',
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

        self._fetch_steps_from_file('user_login.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        print(output)

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome John!',
            'TFA is not enabled! Please enable TFA...',
            'Press enter to proceed...',
            'Prepare your phone and be ready to scan an image with your authentication app.',
            'After that, input the code to verify the setup.',
            'Press enter to continue...',
            'Enter the code: ',
            'OTP secrest is saved.',
            'Success! Press enter to go to homepage.',
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
            'Please select a menu: '
        ]

    def test_add_data(self):
        '''
        Test the scenario of adding data
        '''
        input_values = []
        output = []

        self._fetch_steps_from_file('add_data.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        inserted_id = self._extract_uuid('___'.join(output))
        inserted_datetime = self._extract_datetime('____'.join(output))

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome John!',
            'Enter your MFA code: ',
            'Hi John! You are logged in! Press any key to continue...',
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
            'Enter data value:',
            'Enter data details:',
            self._replace_uuid(inserted_id, 'Data (id:ec6f030c-d16c-450e-b0b1-52e7a7b5152c) is added'),
            'Press any key to proceed: ',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                inserted_id,
                self._replace_datetime(
                    inserted_datetime,
                    '|f4b4950a-27da-4d44-bba8-dcf3ccc5b34d  1234                This is sample data!                              True   Thu, 19 May 2022 04:05:58 GMT |'
                ),
            ),
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

    def test_update_data(self):
        '''
        Test the scenario of updateing data
        '''
        input_values = []
        output = []

        self._fetch_steps_from_file('update_data.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        updated_id = self._extract_uuid('___'.join(output))
        before_update_datetime = self._extract_datetime('____'.join(output))
        updated_datetime = self._extract_datetime('____'.join(output), False)

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome John!',
            'Enter your MFA code: ',
            'Hi John! You are logged in! Press any key to continue...',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                updated_id,
                self._replace_datetime(
                    before_update_datetime,
                    '|eba01383-6d35-4d39-8b39-68b0878eec88  1234                This is sample data!                              True   Thu, 19 May 2022 04:58:00 GMT |'
                ),
            ),
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
            'LIST OF CURRENT DATA ENTRIES:',
            '',
            '============================================================================================================================================================',
            '|ID        Data ID                               Data Value          Data Details                                      Valid  Last Modified         |',
            '|--------------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                updated_id,
                self._replace_datetime(
                    before_update_datetime,
                    '|1         eba01383-6d35-4d39-8b39-68b0878eec88  1234                This is sample data!                              Thu, 19 May 2022 04:58:00 GMT |',
                ),
            ),
            '============================================================================================================================================================',
            'Which data do you want to update?', 'Please Enter the Data ID as displayed in the Data View:',
            '',
            'I want to update... (1)data value (2)data details:',
            'Please Enter 1 or 2: ',
            'Enter new data value. (Number only): ',
            self._replace_uuid(
                updated_id,
                'Data id eba01383-6d35-4d39-8b39-68b0878eec88 is updated by user 1 - data value: 4321!'
            ),
            'Press any key to proceed: ',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                updated_id,
                self._replace_datetime(
                    updated_datetime,
                    '|eba01383-6d35-4d39-8b39-68b0878eec88  4321                This is sample data!                              True   Thu, 19 May 2022 04:58:04 GMT |'
                ),
            ),
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
            'Please select a menu: '
        ]

    def test_download_data(self):
        '''
        Test the scenario of downloading data
        '''
        input_values = []
        output = []

        self._fetch_steps_from_file('download_data.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        existing_id = self._extract_uuid('___'.join(output))
        existing_datetime = self._extract_datetime('____'.join(output))

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome John!',
            'Enter your MFA code: ',
            'Hi John! You are logged in! Press any key to continue...',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                existing_id,
                self._replace_datetime(
                    existing_datetime,
                    '|710f0683-120a-4908-a961-9dfa89d93cff  4321                This is sample data!                              True   Thu, 19 May 2022 05:34:20 GMT |'
                ),
            ),
            '=========================================================================================================================================================',
            'What action you would like to take?', '========================================',
            '',
            '1. Add Data',
            '2. Update Data',
            '3. Delete Data ',
            '4. Download Data\n',
            '5. Logout\n',
            'Please select a menu: ',
            'Data downloaded.',
            'Press any key to continue...',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                existing_id,
                self._replace_datetime(
                    existing_datetime,
                    '|710f0683-120a-4908-a961-9dfa89d93cff  4321                This is sample data!                              True   Thu, 19 May 2022 05:34:20 GMT |',
                ),
            ),
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
            'Please select a menu: '
        ]

    def test_delete_data(self):
        '''
        Test the scenario of deleting data
        '''
        input_values = []
        output = []

        self._fetch_steps_from_file('delete_data.txt', input_values)

        MainApp.input = lambda s: self._mock_input(s, input_values, output)
        MainApp.getpass = lambda s: self._mock_input(s, input_values, output)
        MainApp.print = lambda s : output.append(s)

        with pytest.raises(SystemExit) as e:
            MainApp.MainApp()
            assert e.type == SystemExit
            assert e.value.code != 1

        deleted_id = self._extract_uuid('___'.join(output))
        deleted_datetime = self._extract_datetime('____'.join(output))

        assert output == [
            'Welcome!\n',
            '1. Login',
            '2. Register\n',
            '0. Exit\n',
            'Please select a menu: ',
            'Enter your email: ',
            'Enter your password: ',
            'Welcome John!',
            'Enter your MFA code: ',
            'Hi John! You are logged in! Press any key to continue...',
            '========================================', '***Data View***', '========================================',
            '',
            '=========================================================================================================================================================',
            '|Data ID                               Data Value          Data Details                                      Valid  Last Modified                 |',
            '|-----------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                deleted_id,
                self._replace_datetime(
                    deleted_datetime,
                    '|72cf11e1-8388-4989-b250-74202d5f1f2f  4321                This is sample data!                              True   Thu, 19 May 2022 05:42:52 GMT |',
                ),
            ),
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
            'LIST OF CURRENT DATA ENTRIES:',
            '',
            '============================================================================================================================================================',
            '|ID        Data ID                               Data Value          Data Details                                      Valid  Last Modified         |',
            '|--------------------------------------------------------------------------------------------------------------------------------------------------------|',
            self._replace_uuid(
                deleted_id,
                self._replace_datetime(
                    deleted_datetime,
                    '|1         72cf11e1-8388-4989-b250-74202d5f1f2f  4321                This is sample data!                              Thu, 19 May 2022 05:42:52 GMT |',
                ),
            ),
            '============================================================================================================================================================',
            'Which data entry do you want to delete?',
            'Please Enter the Data ID as displayed in the Data View: ',
            '',
            self._replace_uuid(
                deleted_id,
                'Data id 72cf11e1-8388-4989-b250-74202d5f1f2f is deleted by user 1!'
            ),
            'Press any key to proceed: ',
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
