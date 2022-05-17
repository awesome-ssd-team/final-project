# pylint: disable=invalid-name
'''The main application module'''
from getpass import getpass
from datetime import datetime, timedelta
from tabulate import tabulate

import uuid
import os
import sys
import json
import requests
import pyotp
import qrcode
import pandas as pd
from styleframe import StyleFrame, Styler

class MainApp:
    '''The main application'''
    def __init__(self):
        now = datetime.now()
        expired_at = now + timedelta(minutes=30)
        self.session = {
            'id': str(uuid.uuid4()),
            'start_at': now,
            'start_at_str': now.strftime("%Y-%m-%dT%H:%M:%S"),
            'expired_at': expired_at,
            'expired_at_str': expired_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.user = {
            'id': None,
            'name': None,
            'auth_token': None,
            'is_admin': None
        }
        self.is_blocked = False
        self.homepage()

    def switch_menu(self, activity, **kwargs):
        '''Switch menu based on the current activity'''

        os.system('cls' if os.name == 'nt' else 'clear')

        if self.is_blocked:
            input("You are blocked from doing anything..")
            return self.homepage()

        if activity == 'manage_users':
            return self.manage_users()
        elif activity == 'homepage':
            return self.homepage()
        elif activity == 'register':
            return self.registration_page()
        elif activity == 'login':
            return self.login_page()
        elif activity == 'setup_tfa':
            return self.setup_tfa(**kwargs)
        elif activity == 'action':
            return self.action_page()
        elif activity == 'add':
            return self.add_page()
        elif activity == 'update':
            return self.update_page(**kwargs)
        elif activity == 'delete':
            return self.delete_data(**kwargs)
        elif activity == 'download':
            return self.download_page()

    def homepage(self):
        '''Display the home page'''
        print('Welcome!\n')
        print('1. Login')
        print('2. Register\n')
        print('0. Exit\n')
        mapped_user_input = 3

        # Repeat until valid input
        while mapped_user_input not in [0, 1, 2]:
            user_input = input('Please select a menu: ')

            input_dict = {
                '0': 0,
                '1': 1,
                '2': 2
            }

            mapped_user_input = input_dict.get(user_input) if input_dict.get(user_input) else 3

            if mapped_user_input == 3:
                print('Invalid input..')

        if mapped_user_input == 0:
            sys.exit(0)

        mapped_user_input = str(mapped_user_input)

        menu_dict = {
            '1': 'login',
            '2': 'register'
        }

        return self.switch_menu(menu_dict[mapped_user_input])

    def action_page(self):
        '''Display the data view'''
        status_code = None

        while status_code != 200:

            http_payload = {
                "user_id": self.user['id']
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/retrieve_data_fx',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            # message = response.get('message')
            data = response.get('data')
            if data:
                printed_data = [ i.values() for i in data]
                printed_headers = list(data[0].keys())
                print('\n', tabulate(printed_data, headers=printed_headers, tablefmt="pretty"))
            else:
                print("Try adding some data to see the magic here ;)")



        '''Display the action page'''
        # print('='*40)
        print(f"\nHi {self.user['name']}! (user_id: {self.user['id']})")
        print("What action you would like to take?")
        # print('='*40)
        print()
        print('1. Add Data')
        print('2. Update Data')
        print('3. Delete Data ')

        if self.user.get('is_admin'):
            print('4. Download Data')
            print('5. Manage Users')
        else:
            print('4. Download Data')

        user_action_input = '0'

        available_menu = [1, 2, 3, 4, 5] if self.user.get('is_admin') else [1, 2, 3, 4]

        menu_dict = {
            '1': 'add',
            '2': 'update',
            '3': 'delete',
            '4': 'download',
            '5': 'manage_users'
        } if self.user.get('is_admin') else {
            '1': 'add',
            '2': 'update',
            '3': 'delete',
            '4': 'download'
        }

        # Repeat until valid input
        select_main_menu_input_passed = False

        while select_main_menu_input_passed is False:

            user_action_input = input('Please select a menu: ')

            if user_action_input.isdigit():
                if int(user_action_input) not in available_menu:
                    print("Selection is out of range. Aiming for the moon eh?")
                    continue
                else:
                    select_main_menu_input_passed = True
            elif not user_action_input.isdigit():
                print("Selection should be numerical.")
                continue
            else:
                print("I don't understand your selection =(")
                continue

        self.user['user_business_data'] = data

        return self.switch_menu(activity=menu_dict[user_action_input])

    def registration_page(self):
        '''Display the registration page'''

        status_code = None

        while status_code != 200:
            user_full_name = input('Your full name: ')
            user_email = input('Your email: ')

            user_password = 'a'
            user_password_confirm = 'b'

            while user_password_confirm != user_password:
                user_password = getpass("Enter your password: ")
                user_password_confirm = getpass("Confirm your password: ")

                if user_password != user_password_confirm:
                    print("Password doesn't match!")

            user_secondary_password = 'a'
            user_secondary_password_confirm = 'b'

            while user_secondary_password != user_secondary_password_confirm:
                user_secondary_password = getpass('Set a secondary password: ')
                user_secondary_password_confirm = getpass('Confirm your secondary password: ')

                if user_secondary_password != user_secondary_password_confirm:
                    print("Secondary password doesn't match!")

            http_payload = {
                "full_name": user_full_name,
                "email": user_email,
                "password": user_password,
                "secondary_password": user_secondary_password
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/register_user',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            print(message)

        setup_tfa = ''

        while setup_tfa.lower() not in ['y', 'n']:
            print("We suggest you to setup Two Factor Authorization (TFA) to secure your account.")
            setup_tfa = input("Do you want to set it up now? (y/n): ")

        if setup_tfa == 'y':
            return self.switch_menu(activity='setup_tfa', user_email=user_email)

        # Comment out because it is an unused variable
        # user_input = input('Press enter to go back to homepage...')
        return self.switch_menu('homepage')

    def login_page(self):
        '''Display the login page'''
        status_code = 0
        attempt = 0
        is_tfa_enabled = False

        #Display the input prompt for email and password
        while status_code != 200 and attempt < 3:
            email = input("Enter your email: ")
            password = getpass(prompt="Enter your password: ")

            http_payload = {
                'email': email,
                'password': password,
                'session_id': self.session['id']
            }

            #Sending the payload to cloud function
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/user_login_fix',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')
            data = response.get('data')
            print(message)

            # Save user details to variables if the login is successful
            if status_code == 200:
                print(data)
                tmp_auth_token = data.get("auth_token")
                tmp_user_id = data.get('user_id')
                tmp_user_name = data.get('user_name')
                is_tfa_enabled = data.get('is_tfa_enabled')
                is_admin = int(data.get('is_admin'))

                if is_tfa_enabled:
                    http_payload = {
                        'user_id': tmp_user_id
                    }

                    http_response = requests.post(
                        'https://us-central1-ssd-136542.cloudfunctions.net/verify_otp',
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(http_payload)  # possible request parameters
                    )

                    response = json.loads(http_response.content)
                    status_code = response.get('code')
                    # message = response.get('message') # Comment out because it is an unused variable
                    data = response.get('data')
                    tfa_secret = data.get('tfa_secret')
                    print(tfa_secret)

                    totp = pyotp.TOTP(tfa_secret)
                    passed = False
                    totp_attempt = 0

                    while not passed and totp_attempt < 3:
                        print(str(totp.now()))
                        totp_input = str(input('Enter your MFA code: '))

                        if str(totp_input) == str(totp.now()):
                            passed = True
                        else:
                            print("You entered the wrong code. Please try again.")

                        totp_attempt = totp_attempt + 1

                    if passed:
                        self.user['auth_token'] = tmp_auth_token
                        self.user['id'] = tmp_user_id
                        self.user['name'] = tmp_user_name
                        self.user['is_admin'] = bool(is_admin) if is_admin else False

                        print(f"Hi {self.user['name']}! You are logged in, yay!")
                        input('Success! Press enter to proceed.')

                        return self.switch_menu(activity='action')
                    else:
                        input("Max attempt reached. Returning to homepage...")
                else:
                    print('TFA is not enabled! Please enable TFA...')
                    input('Press enter to proceed...')
                    return self.switch_menu(
                        activity='setup_tfa',
                        user_email=email,
                        tmp_auth_token=tmp_auth_token,
                        user_id=tmp_user_id,
                        user_name=tmp_user_name,
                        is_admin=is_admin
                    )

            if status_code == 401:
                input(message)
                self.is_blocked = True
                return self.switch_menu('homepage')

            if status_code == 200 and is_tfa_enabled:
                # Comment out because it is an unused variable
                # query = (
                #     f"""
                #     SELECT tfa_scret FROM secured.users
                #     WHERE user_id = {self.user_id}
                #     """
                # )

                http_payload = {
                    'user_id': self.user['id']
                }

                http_response = requests.post(
                    'https://us-central1-ssd-136542.cloudfunctions.net/verify_otp',
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(http_payload)  # possible request parameters
                )

                response = json.loads(http_response.content)
                status_code = response.get('code')
                # message = response.get('message') # Comment out because it is an unused variable
                data = response.get('data')
                tfa_secret = data.get('tfa_secret')
                print(tfa_secret)

                totp = pyotp.TOTP(tfa_secret)
                passed = False
                totp_attempt = 0

                while not passed and totp_attempt < 3:
                    print(str(totp.now()))
                    totp_input = str(input('Enter your MFA code: '))

                    if str(totp_input) == str(totp.now()):
                        passed = True
                    else:
                        print("You entered the wrong code. Please try again.")

                    totp_attempt = totp_attempt + 1

                if passed:
                    self.user['auth_token'] = tmp_auth_token
                    print(f"Hi {self.user['name']}! You are logged in, yay!")
                    input('Success! Press enter to proceed.')
                    return self.switch_menu(activity='action')
            elif status_code == 200 and not is_tfa_enabled:
                print('TFA is not enabled! Please enable TFA...')
                input('Press enter to proceed...')
                return self.switch_menu(activity='setup_tfa', user_email=email, tmp_auth_token=tmp_auth_token)

        attempt = attempt + 1
        print("Failed login attempt. Returning to homepage.")
        input('Press enter to proceed.')
        return self.switch_menu(activity='homepage')

    def setup_tfa(self, **kwargs):
        '''Set up the two factor authentication for users'''
        user_email = kwargs.get('user_email')
        tmp_auth_token = kwargs.get('tmp_auth_token')
        user_name = kwargs.get('user_name')
        user_id = kwargs.get('user_id')
        is_admin = kwargs.get('is_admin')
        base32secret = kwargs.get('base32secret')

        is_retry = True if base32secret else False
        base32secret = base32secret if base32secret else pyotp.random_base32()

        totp_uri = pyotp.totp.TOTP(base32secret).provisioning_uri(
            user_email,
            issuer_name="Secure App")

        # Creating an instance of qrcode
        qr_code = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
        qr_code.add_data(totp_uri)
        qr_code.make(fit=True)
        img = qr_code.make_image(fill='black', back_color='white')

        totp = pyotp.TOTP(base32secret)
        print("Prepare your phone and be ready to scan an image with your authentication app.")
        print("After that, input the code to verify the setup.")
        input("Press enter to continue...")
        img.show()

        passed = False
        attempt = 0

        while passed is False and attempt < 3:
            otp_input = input("Enter the code: ")

            if str(otp_input) != str(totp.now()):
                print("The entered code is wrong, please try again.")
            else:
                passed = True

            attempt = attempt + 1

            if attempt == 3 and not is_retry:
                input("Let's try again from the beginning..")
                return self.switch_menu(activity='setup_tfa', user_email=user_email, base32secret=base32secret)
            elif attempt == 3 and is_retry:
                input("Setup TFA failed. Try logging in to retry the setup..")
                return self.switch_menu(activity='homepage')

        # Save the secret to DB for further authentication
        http_payload = {
            'otp_secret': base32secret,
            'email': user_email
        }

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/setup_otp',
            headers={"Content-Type": "application/json"},
            data=json.dumps(http_payload)  # possible request parameters
        )

        response = json.loads(http_response.content)
        message = response.get('message')

        print(message)

        if user_id and user_name:
            self.user['id'] = user_id
            self.user['name'] = user_name
            self.user['is_admin'] = is_admin

        if not tmp_auth_token:
            input('Success! Press enter to go to homepage.')
            return self.switch_menu(activity='homepage')
        else:
            input("Yay, TFA setup, let's continue!")
            self.user['auth_token'] = tmp_auth_token
            return self.switch_menu(activity='action')

    def add_page(self):
        '''Display the add data page'''
        status_code = 0
        data_value = 0
        data_details = ''

        while status_code != 200:
            #Loop until valid input is received
            while not data_value:
                data_value = input("Enter data value (numerical):")
                if not data_value.isdigit():
                    print("Data value must be number")
                    data_value = 0
                    continue
            while not data_details:
                data_details = input("Enter data details:")

            http_payload = {
                "user_id": self.user['id'],
                'data_value': int(data_value),
                'data_details': data_details
            }

            #Send payload to cloud function to add data for a specific user
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/add_data_fix',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            #Extract the information returned from cloud function
            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')
            print(message)

        input("Press any key to proceed: ")
        return self.switch_menu(activity='action')

    def update_page(self, **kwargs):
        '''Display the update page'''

        user_business_data = self.user.get('user_business_data')
        total_data = len(user_business_data)

        if total_data == 0:
            print("No active data entries for this user.")
            input("Press any key to return...")
            return self.switch_menu(activity='action')

        printed_data = [i.values() for i in user_business_data]
        printed_headers = list(user_business_data[0].keys())
        distinct_data_id = [str(i.get('data_id')) for i in user_business_data]

        print(tabulate(printed_data, headers=printed_headers, tablefmt="pretty"))

        status_code = 0
        update_action = 0
        data_value = 0
        data_details = 'text'
        data_id = 0

        while status_code != 200:
            print("Which data do you want to update?")

            # Loop until a valid input is received
            data_id_select_passed = False

            while data_id_select_passed is False:
                data_id = input("Please Enter the Data ID as displayed in the Data View: ")

                # Check if the input data_id is valid
                if not data_id.isdigit():
                    print("Invalid ID entered. It should be a digit.")
                    continue
                elif data_id not in distinct_data_id:
                    print("You have no data with such ID..")
                    continue

                data_id_select_passed = True

            print()

            # Loop until a valid update action item is received
            while not update_action:
                print("I want to update...", '\n' * 2, "(1) Data Value", '\n', "(2) Data Details", '\n')
                update_action = input("Please Enter 1 or 2: ")
                if not update_action.isdigit() or int(update_action) not in [1, 2]:
                    print('Input is invalid...\n')
                    update_action = 0
                    continue

            if update_action == '1':
                while not data_value:
                    data_value = input("Enter new data value. (Number only): ")
                    if not data_value.isdigit():
                        print("Data value can only be number")
                        data_value = 0
                        continue
            elif update_action == '2':
                data_details = input("Enter new data details: ")

            http_payload = {
                "user_id": self.user['id'],
                'data_id': data_id,
                'update_action': update_action,
                'data_value': data_value,
                'data_details': data_details
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/update_data_fix',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            #print(status_code)
            print(message)

        next = input("Press any key to proceed: ")
        return self.switch_menu(activity='action')

    def delete_data(self, **kwargs):
        '''Display the delete_data page'''

        user_business_data = self.user.get('user_business_data')
        total_data = len(user_business_data)

        if total_data == 0:
            print("No active data entries for this user.")
            input("Press any key to return...")
            return self.switch_menu(activity='action')

        printed_data = [i.values() for i in user_business_data]
        printed_headers = list(user_business_data[0].keys())
        distinct_data_id = [str(i.get('data_id')) for i in user_business_data]

        print(tabulate(printed_data, headers=printed_headers, tablefmt="pretty"))

        if total_data == 0:
            print("No active data entries for this user.")
            input("Press any key to return...")
            return self.switch_menu(activity='action')

        # Loop until a valid input is received
        data_id_select_passed = False

        while data_id_select_passed is False:
            data_id = input("Please Enter the Data ID as displayed in the Data View: ")

            # Check if the input data_id is valid
            if not data_id.isdigit():
                print("Invalid ID entered. It should be a digit.")
                continue
            elif data_id not in distinct_data_id:
                print("You have no data with such ID..")
                continue

            data_id_select_passed = True

        http_payload = {
            "user_id": self.user['id'],
            'data_id': data_id,
            'update_action': '3',
        }

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/update_data_fix',
            headers={"Content-Type": "application/json"},
            data=json.dumps(http_payload)  # possible request parameters
        )

        response = json.loads(http_response.content)
        status_code = response.get('code')
        message = response.get('message')

        print(status_code, message)

        input("Press any key to proceed: ")
        return self.switch_menu(activity='action')


    def download_page(self):
        '''Display the download page'''
        status_code = 0

        while status_code != 200:
            http_payload = {
                "user_id": self.user['id']
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/download_data_fix',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            data = response.get('data')

            if len(data) == 0:
                print("No data is available for download")
            else:
                #Convert data to excel format
                df = pd.DataFrame(data)
                file_name = f'{self.user["name"]}_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
                df.to_excel(
                    file_name,
                    sheet_name='business_data'
                )
                # cols = df.columns.tolist()
                # cols = cols[1:2] + cols[:1] + cols[2:]
                # df = df[cols]
                # df.rename(columns= {"data_id":"Data ID","data_details":"Data Details","data_value":"Data Value","is_valid":"Valid?","last_modified":"Last modified"}, inplace=True)
                # df.style.set_properties(align="left")
                # timestamp = datetime.now()
                # excel_writer = StyleFrame.ExcelWriter(f'{self.user["name"]}_{timestamp}.xlsx')
                # sf = StyleFrame(df)
                # sf.set_column_width(columns=['Data ID','Data Details','Last modified'],width=40)
                # sf.set_column_width(columns=['Data Value'],width=20)
                # sf.apply_column_style(cols_to_style=['Data ID','Data Details','Data Value','Last modified'],styler_obj=Styler(horizontal_alignment='left'),style_header=True)
                # sf.to_excel(excel_writer=excel_writer)
                # excel_writer.save()
                print("Data downloaded.")

        input('Press any key to continue...')
        return self.switch_menu(activity='action')

    def manage_users(self):

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/retrieve_user_data_fix',
            headers={"Content-Type": "application/json"},
            data=json.dumps({})
        )

        response = json.loads(http_response.content)
        data = response.get('data')

        printed_data = [i.values() for i in data]
        printed_headers = list(data[0].keys())

        distinct_user_id = [str(i.get('user_id')) for i in data]

        print(tabulate(printed_data, headers=printed_headers, tablefmt="pretty"))

        user_selection_passed = False

        while user_selection_passed is False:
            manage_user_id = input("Which user_id you want to manage? ")

            if manage_user_id.isdigit():
                if manage_user_id in distinct_user_id:
                    user_selection_passed = True
                else:
                    print("user_id is not registered.")
                    continue
            else:
                print("Selection should be digits.")

        for i in data:
            if str(i.get('user_id')) == manage_user_id:
                selected_user_data = i
                break

        os.system('cls' if os.name == 'nt' else 'clear')

        printed_data = [selected_user_data.values()]
        printed_headers = selected_user_data.keys()

        print(tabulate(printed_data, headers=printed_headers, tablefmt="pretty"))

        print(f"Selected user_id: {manage_user_id}.\n")

        print("1. Change active status")
        print("2. Change role\n")

        select_user_operation_passed = False

        while select_user_operation_passed is False:
            user_operation = input("What do you want to do about it: ")

            if user_operation.isdigit():
                if user_operation in ['1', '2']:
                    select_user_operation_passed = True
                else:
                    print("Invalid operation selection.")
                    continue
            else:
                print("Selection is not recognized.")
                continue

        operation_dict = {
            "1": {
                'column': 'is_active',
                'existing_value': bool(int(selected_user_data.get('is_active'))),
                'new_value': not (bool(int(selected_user_data.get('is_active'))))
            },
            "2": {
                'column': 'is_admin',
                'existing_value': bool(int(selected_user_data.get('is_admin'))),
                'new_value': not (bool(int(selected_user_data.get('is_admin'))))
            }
        }

        operation_data = operation_dict.get(user_operation)

        os.system('cls' if os.name == 'nt' else 'clear')

        confirmation_passed = False
        while not confirmation_passed:
            confirmation = input(
                "Are you sure you want to change {0} column of user_id {1} from {2} to {3}? (N/y)\n"
                .format(
                    operation_data.get('column'),
                    manage_user_id,
                    operation_data.get('existing_value'),
                    operation_data.get('new_value')
                )
            )

            if confirmation.lower() not in ['y', 'n']:
                print("Please confirm with y or n.")
                continue
            else:
                confirmation_passed = True

        http_payload = {
            'user_id': manage_user_id,
            'column': operation_data.get('column'),
            'value': operation_data.get('new_value')
        }

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/manage_user_fix',
            headers={"Content-Type": "application/json"},
            data=json.dumps(http_payload)  # possible request parameters
        )

        response = json.loads(http_response.content)
        status_code = response.get('code')
        message = response.get('message')
        print(message)
        input("Returning to homepage. Press enter to proceed.")

        return self.switch_menu(activity='action')



