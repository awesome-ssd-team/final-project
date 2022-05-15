# pylint: disable=invalid-name
'''The main application module'''
from getpass import getpass
from datetime import datetime, timedelta

import uuid
import os
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
            self.add_page()
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
            print()
            print("="*153)
            print("|","Data ID".ljust(38),"Data Value".ljust(20),"Data Details".ljust(50),"Valid".ljust(7),"Last Modified".ljust(30),"|")
            print("|","-"*149,"|")
            for item in data:
                data_id=str(item['data_id']).ljust(38)
                data_value=str(item['data_value']).ljust(20)
                data_details=str(item['data_details']).ljust(50)
                is_valid=str(bool(item['is_valid'])).ljust(7)
                last_modified=str(item['last_modified']).ljust(30)
                print("|",data_id,data_value,data_details,is_valid,last_modified,"|")
            print("="*153)

        '''Display the action page'''
        print('='*40)
        print('What action you would like to take?')
        print('='*40)
        print()
        print('1. Add Data')
        print('2. Update Data')
        print('3. Delete Data ')
        print('4. Download Data\n')
        user_action_input = '0'

        # Repeat until valid input
        while int(user_action_input) not in [1, 2, 3, 4]:
            user_action_input = input('Please select a menu: ')
            if int(user_action_input) not in [1, 2, 3, 4]:
                print('Input is invalid...\n')

        menu_dict = {
            '1': 'add',
            '2': 'update',
            '3': 'delete',
            '4': 'download'
        }
        
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
            message = response.get('message')
            data = response.get('data')
            print(message)

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
                    input('Success! Press enter to proceed.')
                    return self.switch_menu(activity='action')
            else:
                input('Success! Press enter to proceed.')
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

    def add_page(self):
        '''Display the add data page'''
        status_code = 0
        data_value = 0
        data_details = ''


        while status_code != 200:
            while not data_value:
                data_value = input("Enter data value:")
            while not data_details:
                data_details = input("Enter data details:")

            http_payload = {
                "user_id": self.user['id'],
                'data_value': int(data_value),
                'data_details': data_details
            }

            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/add_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')
            print(message)

        input("Press any key to proceed: ")
        return self.switch_menu(activity='action')

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
        id_list = []
        count = 0
        #print('='*40)
        print("="*156)
        print("|","ID".ljust(10), "Data ID".ljust(38),"Data Value".ljust(20),"Data Details".ljust(50),"Valid".ljust(7),"Last Modified".ljust(22),"|")
        print("|","-"*152,"|")
        if response:
            for i in response:
                if i.get('is_valid') == 1:
                    count = count + 1
                    id = str(count).ljust(10)
                    data_id=str(i.get('data_id')).ljust(38)
                    data_value=str(i.get('data_value')).ljust(20)
                    data_details=str(i.get('data_details')).ljust(50)
                    #is_valid=str(i.get('is_valid')).ljust(7)
                    last_modified=str(i.get('last_modified')).ljust(30)
                    print("|",id,data_id,data_value,data_details,last_modified,"|")
                    #print("ID:",count,     "Data_id:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
                    id_list.append(i.get('data_id'))
            print("="*156)
        else:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')
        #print('='*40)

        status_code = 0
        update_action = 0
        data_value = 0
        data_details = 'text'

        is_tfa_enabled = False

        while status_code != 200:
            print("Which data do you want to update?")
            data_id = input("Enter data ID: ") 

            #ADJUST
            while int(data_id) <= 0 or int(data_id) > count: #int(data_id) not in id_list:
                print("Invalid ID entered")
                data_id = input("Please Enter the Data ID as displayed in the Data View:")
            print()
            #http_payload = {
            #    "user_id": self.user['id'],
            #    'data_id': id_list[int(data_id) - 1],#data_id,
            #    'update_action': '3',
            #}
            ###
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
                'data_id': id_list[int(data_id) - 1],
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

        count = 0
        print("="*156)
        print("|","ID".ljust(10), "Data ID".ljust(38),"Data Value".ljust(20),"Data Details".ljust(50),"Valid".ljust(7),"Last Modified".ljust(22),"|")
        print("|","-"*152,"|")
        if response:
            for i in response:
                if i.get('is_valid') == 1:
                    count = count + 1
                    id = str(count).ljust(10)
                    data_id=str(i.get('data_id')).ljust(38)
                    data_value=str(i.get('data_value')).ljust(20)
                    data_details=str(i.get('data_details')).ljust(50)
                    #is_valid=str(i.get('is_valid')).ljust(7)
                    last_modified=str(i.get('last_modified')).ljust(30)
                    print("|",id,data_id,data_value,data_details,last_modified,"|")
                    #print("ID:",count,     "Data_id:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
                    id_list.append(i.get('data_id'))
            print("="*156)
        else:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')


        #print('='*40)
        #count = 0
        #for i in response:
        #    if i.get('is_valid') == 1:
        #        count = count + 1
        #        print("ID:", count, "Data_id:",i.get('data_id'), "     DATA VALUE:", i.get('data_value'), "     DESCRIPTION:", i.get('data_details'))
        #        id_list.append(i.get('data_id'))
        #    else:
        #        print("No active data entries for this user.")
        #        input("Press any key to return...")
        #        self.switch_menu(activity='action')
        #print('='*40)
        status_code = 0
        while status_code != 200:
            print("Which data entry do you want to delete?")
            #DO QUERY HERE TO DISPLAY DATA ENTRIES... OR DO THE QUERY ON TOP...
            data_id = input("Enter the ID: ") 

            while int(data_id) <= 0 or int(data_id) > count: #int(data_id) not in id_list:
                print("Invalid ID entered")
                data_id = input("Please Enter the Data ID as displayed in the Data View:")
            print()
            #send_data = id_list[]
            http_payload = {
                "user_id": self.user['id'],
                'data_id': id_list[int(data_id) - 1],#data_id,
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


    def download_page(self):
        '''Display the download page'''
        status_code = 0

        while status_code != 200:
            http_payload = {
                "user_id": self.user['id']
            }
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/register_user-2',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            data = response.get('data')

            #Convert data to excel format
            df = pd.DataFrame(data)
            cols = df.columns.tolist()
            cols = cols[1:2] + cols[:1] + cols[2:]
            df = df[cols]
            df.rename(columns= {"data_id":"Data ID","data_details":"Data Details","data_value":"Data Value","is_valid":"Valid?","last_modified":"Last modified"}, inplace=True)
            df.style.set_properties(align="left")
            timestamp = datetime.now()
            excel_writer = StyleFrame.ExcelWriter(f'{self.user["name"]}_{timestamp}.xlsx')
            sf = StyleFrame(df)
            sf.set_column_width(columns=['Data ID','Data Details','Last modified'],width=40)
            sf.set_column_width(columns=['Data Value'],width=20)
            sf.apply_column_style(cols_to_style=['Data ID','Data Details','Data Value','Last modified'],styler_obj=Styler(horizontal_alignment='left'),style_header=True)
            sf.to_excel(excel_writer=excel_writer)
            excel_writer.save()

        input('Data downloaded. Press any key to continue...')
        return self.switch_menu(activity='action')


