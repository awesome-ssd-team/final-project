'''The main application module'''
from getpass import getpass
from datetime import datetime, timedelta

import uuid
import os
import json
import requests
import pyotp
import qrcode

class MainApp:
    '''The main application'''
    def __init__(self):
        now = datetime.now()
        expired_at =  now + timedelta(minutes=30)
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
        }
        self.homepage()

    def switch_menu(self, activity, **kwargs):
        '''Switch menu based on the current activity'''

        os.system('cls' if os.name == 'nt' else 'clear')
        #print("KWARGS:",kwargs)
        if activity == 'homepage':
            self.homepage()
        elif activity == 'register':
            self.registration_page()
        elif activity == 'login':
            self.login_page()
        elif activity == 'setup_tfa':
            self.setup_tfa(**kwargs)
        elif activity == 'action':
            self.action_page()
        elif activity == 'add':
            self.setup_tfa()
        elif activity == 'update':
            self.update_page(**kwargs)
        elif activity == 'delete':
            self.delete_data(**kwargs)

    def homepage(self):
        '''Display the home page'''
        print('Welcome!\n')
        print('1. Login')
        print('2. Register\n')
        user_input = '0'

        # Repeat until valid input
        while int(user_input) not in [1, 2]:
            user_input = input('Please select a menu: ')
            if int(user_input) not in [1, 2]:
                print('Input is invalid...\n')

        menu_dict = {
            '1': 'login',
            '2': 'register'
        }

        return self.switch_menu(menu_dict[user_input])

    def action_page(self):
        '''Display the data view'''
        status_code = None

        print('='*40)
        print('***Data View***')
        print('='*40)
        while status_code != 200:

            http_payload = {
                "user_id": self.user['id']
            }

            http_response = requests.post(
                #'https://us-central1-ssd-136542.cloudfunctions.net/register_user',
                'https://us-central1-ssd-136542.cloudfunctions.net/retrieve_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )           

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')
            data = response.get('data')
            kwargs = data
            #print(status_code)
            #print(message)
            print()
            print()
            if data:
                for i in data:
                    print("ID:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
            else:
                print("No data entries for this user.")
            #print(data)
            print()
            print()

        '''Display the action page'''
        print('='*40)
        print('What action you would like to take?')
        print('='*40)
        print()
        print('1. Add Data (Opening soon)')
        print('2. Update Data')
        print('3. Delete Data\n')
        user_action_input = '0'

        # Repeat until valid input
        while int(user_action_input) not in [1, 2, 3]:
            user_action_input = input('Please select a menu: ')
            if int(user_action_input) not in [1, 2, 3]:
                print('Input is invalid...\n')

        menu_dict = {
            '1': 'add',
            '2': 'update',
            '3': 'delete'
        }
        #if user_action_input == '3':
        #    self.delete_data(data)
        #elif user_action_input == '2':
        #    self.update_page(data)
        print("DATA: ",data)
        
        kwargs = {}
        for i in data:
            kwargs[str(i.get('data_id'))]=i
        return self.switch_menu(menu_dict[user_action_input], **kwargs)

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

        while status_code != 200 and attempt < 3:
            email = input("Enter your email: ")
            password = getpass(prompt="Enter your password: ")

            http_payload = {
                'email': email,
                'password': password,
                'session_id': self.session['id'],
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/user_login',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            # message = response.get('message') # Comment out because it is an unused variable
            data = response.get('data')

            if data:
                tmp_auth_token = data.get("auth_token")
                self.user['id'] = data.get('user_id')
                self.user['name'] = data.get('user_name')
                is_tfa_enabled = data.get('is_tfa_enabled')

            if status_code != 200:
                input("You are blocked! Returning to homepage.")
                self.switch_menu('homepage')

            if is_tfa_enabled:
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
                attempt = 0

                while not passed and attempt < 3:
                    print(str(totp.now()))
                    totp_input = str(input('Enter your MFA code: '))

                    if str(totp_input) == str(totp.now()):
                        passed = True
                    else:
                        print("You entered the wrong code. Please try again.")

                    attempt = attempt + 1

                if passed:
                    self.user['auth_token'] = tmp_auth_token
                    print(f"Hi {self.user['name']}! You are logged in, yay!")
                    return self.switch_menu(activity='action')
            attempt = attempt + 1

    def setup_tfa(self, **kwargs):
        '''Set up the two factor authentication for users'''
        user_email = kwargs.get('user_email')
        base32secret = pyotp.random_base32()

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

            if attempt == 3:
                input("Let's try again from the beginning..")
                self.switch_menu(activity='setup_tfa', user_email=user_email)

        # Save the secret to DB for further authentication
        if passed:

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
            input('Success! Press enter to go to homepage.')

        return self.switch_menu(activity='homepage')

    def update_page(self, **kwargs):
        '''Display the update page'''
        response = []
        for key, value in kwargs.items():
            response.append(value)

        print("LIST OF CURRENT DATA ENTRIES:")
        print()
        if not response:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')

        print('='*40)
        for i in response:
            if i.get('is_valid') == 1:
                print("ID:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
                #id_list.append(i.get('data_id'))
            else:
                print("No active data entries for this user.")
                input("Press any key to return...")
                self.switch_menu(activity='action')
        print('='*40)

        status_code = 0
        update_action = 0
        data_value = 0
        data_details = 'text'

        is_tfa_enabled = False

        while status_code != 200:
            print("Which data do you want to update?")
            data_id = input("Enter data ID: ") 

            while int(update_action) not in [1, 2]:
                print("I want to update... (1)data value (2)data details:")
                update_action = input("Please Enter 1 or 2: ")
                if int(update_action) not in [1, 2]:
                    print('Input is invalid...\n')
            
            if update_action == '1':
                data_value = input("Enter new data value. (Number only): ")

                
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
                'https://us-central1-ssd-136542.cloudfunctions.net/update_data',
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
        os.system('cls' if os.name == 'nt' else 'clear')
        #UNPACK KWARGS:
        response = []
        for key, value in kwargs.items():
            response.append(value)

        id_list = []
        print("LIST OF CURRENT DATA ENTRIES:")
        print()
        if not response:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')

        print('='*40)
        for i in response:
            if i.get('is_valid') == 1:
                print("ID:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
                id_list.append(i.get('data_id'))
            else:
                print("No active data entries for this user.")
                input("Press any key to return...")
                self.switch_menu(activity='action')
        print('='*40)

        print()

        status_code = 0

        while status_code != 200:
            print("Which data entry do you want to delete?")
            #DO QUERY HERE TO DISPLAY DATA ENTRIES... OR DO THE QUERY ON TOP...
            data_id = input("Enter data ID: ") 

            while int(data_id) not in id_list:
                print("Invalid ID entered")
                data_id = input("Please Enter the Data ID as displayed in the Data View:")
            print()

            http_payload = {
                "user_id": self.user['id'],
                'data_id': data_id,
                'update_action': '3',
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/update_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )
            
            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            print(message)

        next = input("Press any key to proceed: ")
        return self.switch_menu(activity='action')




        self.action_page()



