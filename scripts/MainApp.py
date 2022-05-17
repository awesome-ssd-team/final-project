# pylint: disable=invalid-name
'''The main application module'''
# Importing the libraries the application needs
from getpass import getpass
from datetime import datetime, timedelta

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
        # Initialize the session and user information
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
        self.is_blocked = False
        self.homepage()

    # Switch to different pages according to user action
    def switch_menu(self, activity, **kwargs):
        '''Switch menu based on the current activity'''

        # Clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')

        # Conditions to check the user action to provide appropriate functions
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
        elif activity == 'download':
            self.download_page()
        elif activity == 'logout':
            # Clear out user information
            self.user = {
            'id': None,
            'name': None,
            'auth_token': None,
            }
            self.homepage()

    # Homepage for user to select login or register
    def homepage(self):
        '''Display the home page for user to login to register'''
        print('Welcome!\n')
        print('1. Login')
        print('2. Register\n')
        print('0. Exit\n')
        user_input = '-1'

        # Repeat input prompt until valid input
        while int(user_input) not in [0, 1, 2]:
            user_input = input('Please select a menu: ')
            # Check if the user is inputting number, if not, prompt user to input correct number
            if not user_input.isdigit():
                print("Please give only the correct option.")
                user_input = '-1'
                continue
            else:
                if int(user_input) not in [0, 1, 2]:
                    print('Input is invalid...\n')

        if int(user_input) == 0:
            sys.exit(0)

        # Store the action in dictionary for switch use
        menu_dict = {
            '1': 'login',
            '2': 'register'
        }

        return self.switch_menu(menu_dict[user_input])

    # Page that allows user to view data and manipulate with data
    def action_page(self):
        '''Display the data view of the user and provides options for user to add, update, delete and download data'''
        status_code = None

        print('='*40)
        print('***Data View***')
        print('='*40)
        while status_code != 200:

            http_payload = {
                "user_id": self.user['id']
            }

            # Retrieving data from cloud function using user id
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/retrieve_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            data = response.get('data')
            kwargs = data
            # Display the data view
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

        # Display the action menu for user
        print('='*40)
        print('What action you would like to take?')
        print('='*40)
        print()
        print('1. Add Data')
        print('2. Update Data')
        print('3. Delete Data ')
        print('4. Download Data\n')
        print('5. Logout\n')
        user_action_input = 0

        # Repeat until valid input
        while not user_action_input:
            user_action_input = input('Please select a menu: ')
            if not user_action_input.isdigit() or int(user_action_input) not in [1, 2, 3, 4,5]:
                print('Input is invalid...\n')
                user_action_input = 0

        menu_dict = {
            '1': 'add',
            '2': 'update',
            '3': 'delete',
            '4': 'download',
            '5': 'logout'
        }

        kwargs = {}
        for i in data:
            kwargs[str(i.get('data_id'))]=i
        return self.switch_menu(menu_dict[user_action_input], **kwargs)

    # Page for user to register
    def registration_page(self):
        '''Display the registration page'''

        status_code = None

        while status_code != 200:
            # Getting user info - name and email
            user_full_name = input('Your full name: ')
            user_email = input('Your email: ')

            # Setting up the first password
            user_password = 'a'
            user_password_confirm = 'b'

            # Loop until the password typed first time matches with the password typed the second time
            # Reduce risk of mistyping password
            while user_password_confirm != user_password:
                user_password = getpass("Enter your password: ")
                user_password_confirm = getpass("Confirm your password: ")

                if user_password != user_password_confirm:
                    print("Password doesn't match!")

            # Setting up the second password
            user_secondary_password = 'a'
            user_secondary_password_confirm = 'b'

            # Loop until the password typed first time matches with the password typed the second time
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

            # Saving the user data into database
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/register_user',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            print(message)

        # Setting up TFA
        setup_tfa = ''

        while setup_tfa.lower() not in ['y', 'n']:
            print("We suggest you to setup Two Factor Authorization (TFA) to secure your account.")
            setup_tfa = input("Do you want to set it up now? (y/n): ")

        # If user selects yes, he/she will be directed to the set up tfa page
        if setup_tfa == 'y':
            return self.switch_menu(activity='setup_tfa', user_email=user_email)
        # else the user will be directed back to the homepage
        return self.switch_menu('homepage')

    # Login page for user to login
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
                'https://us-central1-ssd-136542.cloudfunctions.net/user_login',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')
            data = response.get('data')
            print(message)

            #Save user details to variables if the login is successful
            if status_code == 200:
                tmp_auth_token = data.get("auth_token")
                self.user['id'] = data.get('user_id')
                self.user['name'] = data.get('user_name')
                is_tfa_enabled = data.get('is_tfa_enabled')

            if status_code != 200 and attempt == 3:
                input("You are blocked! Returning to homepage.")
                self.is_blocked = True
                self.switch_menu('homepage')

            # For user with TFA enable, check if the MFA code matches
            if status_code == 200 and is_tfa_enabled:
                http_payload = {
                    'user_id': self.user['id']
                }

                # Getting the tfa secret saved in the database when setting up TFA
                http_response = requests.post(
                    'https://us-central1-ssd-136542.cloudfunctions.net/verify_otp',
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(http_payload)
                )

                response = json.loads(http_response.content)
                status_code = response.get('code')
                data = response.get('data')
                tfa_secret = data.get('tfa_secret')

                # Generate the MFA code
                totp = pyotp.TOTP(tfa_secret)
                passed = False
                attempt = 0

                # User has 3 chances to imput the correct MFA code
                while not passed and attempt < 3:
                    totp_input = str(input('Enter your MFA code: '))

                    if str(totp_input) == str(totp.now()):
                        passed = True
                    else:
                        print("You entered the wrong code. Please try again.")

                    attempt = attempt + 1

                if passed:
                    self.user['auth_token'] = tmp_auth_token
                    input(f"Hi {self.user['name']}! You are logged in! Press any key to continue...")
                    return self.switch_menu(activity='action')
            # Prompt user to set up TFA if not yet set up
            elif status_code == 200 and not is_tfa_enabled:
                print('TFA is not enabled! Please enable TFA...')
                input('Press enter to proceed...')
                return self.switch_menu(activity='setup_tfa', user_email=email, tmp_auth_token=tmp_auth_token)

        # Failure in login and redirect the user back to homepage
        attempt = attempt + 1
        print("Failed login attempt. Returning to homepage.")
        input('Press enter to proceed.')
        return self.switch_menu(activity='homepage')

    # Page for user to set up TFA
    def setup_tfa(self, **kwargs):
        '''Set up the two factor authentication for users'''
        user_email = kwargs.get('user_email')
        tmp_auth_token = kwargs.get('tmp_auth_token')
        base32secret = kwargs.get('base32secret')

        # Generate a base32 string secret for later MFA set up
        is_retry = True if base32secret else False
        base32secret = base32secret if base32secret else pyotp.random_base32()

        # Generate the URI for the qr code that user scans
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
        # Show the QR code image to user to scan
        img.show()

        passed = False
        attempt = 0

        # Verify the user's device is generating the correct code
        while passed is False and attempt < 3:
            otp_input = input("Enter the code: ")

            if str(otp_input) != str(totp.now()):
                print("The entered code is wrong, please try again.")
            else:
                passed = True

            attempt = attempt + 1

            if attempt == 3 and not is_retry:
                input("Let's try again from the beginning..")
                self.switch_menu(activity='setup_tfa', user_email=user_email, base32secret=base32secret)
            elif attempt == 3 and is_retry:
                input("Setup TFA failed. Try logging in to retry the setup..")
                self.switch_menu(activity='homepage')

        # Save the secret to DB for further authentication
        http_payload = {
            'otp_secret': base32secret,
            'email': user_email
        }

        http_response = requests.post(
            'https://us-central1-ssd-136542.cloudfunctions.net/setup_otp',
            headers={"Content-Type": "application/json"},
            data=json.dumps(http_payload)
        )

        response = json.loads(http_response.content)
        message = response.get('message')

        print(message)

        if not tmp_auth_token:
            input('Success! Press enter to go to homepage.')
            return self.switch_menu(activity='homepage')
        else:
            input('Success! Press enter to go to homepage.')
            self.user['auth_token'] = tmp_auth_token
            return self.switch_menu(activity='action')

    # Page for user to add data
    def add_page(self):
        '''Display the add data page'''
        status_code = 0
        data_value = 0
        data_details = ''

        while status_code != 200:
            #Loop until valid input is received
            while not data_value:
                data_value = input("Enter data value:")
                if not data_value.isdigit():
                    print("Data value must be number")
                    data_value=0
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
                'https://us-central1-ssd-136542.cloudfunctions.net/add_data',
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

    # Page for user to update his/her business data
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
        print("="*156)
        print("|","ID".ljust(10), "Data ID".ljust(38),"Data Value".ljust(20),"Data Details".ljust(50),"Valid".ljust(7),"Last Modified".ljust(22),"|")
        print("|","-"*152,"|")

        #Format the response to make it more readable
        if response:
            for i in response:
                if i.get('is_valid') == 1:
                    count = count + 1
                    id = str(count).ljust(10)
                    data_id=str(i.get('data_id')).ljust(38)
                    data_value=str(i.get('data_value')).ljust(20)
                    data_details=str(i.get('data_details')).ljust(50)
                    last_modified=str(i.get('last_modified')).ljust(30)
                    print("|",id,data_id,data_value,data_details,last_modified,"|")
                    id_list.append(i.get('data_id'))
            print("="*156)
        else:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')

        status_code = 0
        update_action = 0
        data_value = 0
        data_details = 'text'
        data_id = 0

        while status_code != 200:
            print("Which data do you want to update?")

            #Loop until a valid input is received
            while not data_id:
                data_id = input("Please Enter the Data ID as displayed in the Data View:")
                #Check if the input data_id is valid
                if not data_id.isdigit() or int(data_id) <= 0 or int(data_id) > count:
                    print("Invalid ID entered")
                    data_id = 0
                    continue
            print()

            #Loop until a valid update action item is received
            while not update_action:
                print("I want to update... (1)data value (2)data details:")
                update_action = input("Please Enter 1 or 2: ")
                if not update_action.isdigit() or int(update_action) not in [1, 2]:
                    print('Input is invalid...\n')
                    update_action = 0
                    continue

            # Check user whether data value or data details needs to be updated
            if update_action == '1':
                while not data_value:
                    data_value = input("Enter new data value. (Number only): ")
                    if not data_value.isdigit():
                        print("Data value can only be number")
                        data_value=0
                        continue
            elif update_action == '2':
                data_details = input("Enter new data details: ")

            http_payload = {
                "user_id": self.user['id'],
                'data_id': id_list[int(data_id) - 1],
                'update_action': update_action,
                'data_value': data_value,
                'data_details': data_details
            }

            # Sending request to cloud function to update the data
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/update_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            print(message)

        # Action finishes and redirect user back to action menu
        input("Press any key to proceed: ")
        return self.switch_menu(activity='action')

    # Page for user to delete data
    def delete_data(self, **kwargs):
        '''Display the delete_data page'''
        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        #Unpack kwargs:
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
        #Format response to more readable
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
                    last_modified=str(i.get('last_modified')).ljust(30)
                    print("|",id,data_id,data_value,data_details,last_modified,"|")
                    id_list.append(i.get('data_id'))
            print("="*156)
        else:
            print("No active data entries for this user.")
            input("Press any key to return...")
            self.switch_menu(activity='action')


        status_code = 0
        data_id = 0
        while status_code != 200:
            print("Which data entry do you want to delete?")
            # Getting the data_id that user wants to delete
            while not data_id:
                data_id = input("Please Enter the Data ID as displayed in the Data View: ")
                if not data_id.isdigit() or int(data_id) <= 0 or int(data_id) > count:
                    print("Invalid ID entered")
                    data_id = 0
                    continue
            print()
            http_payload = {
                "user_id": self.user['id'],
                'data_id': id_list[int(data_id) - 1],
                'update_action': '3',
            }

            # Sending request to cloud function to update data is_valid to false
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/update_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)  # possible request parameters
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            message = response.get('message')

            print(message)

        input("Press any key to proceed: ")
        return self.switch_menu(activity='action')


    # Page to user to download his/her data
    def download_page(self):
        '''Display the download page'''
        status_code = 0

        while status_code != 200:
            http_payload = {
                "user_id": self.user['id']
            }

            #Retrieving data from cloud function
            http_response = requests.post(
                'https://us-central1-ssd-136542.cloudfunctions.net/retrieve_data',
                headers={"Content-Type": "application/json"},
                data=json.dumps(http_payload)
            )

            response = json.loads(http_response.content)
            status_code = response.get('code')
            data = response.get('data')

            # If no data is returned, abort action and redirect user back to action menu
            if len(data)==0:
                print("No data is available for download")
            else:
                #Convert data to excel format
                df = pd.DataFrame(data)
                cols = df.columns.tolist()
                # Reorder the columns
                cols = cols[1:2] + cols[:1] + cols[2:]
                df = df[cols]
                # Style the excel
                df.rename(columns= {"data_id":"Data ID","data_details":"Data Details","data_value":"Data Value","is_valid":"Valid?","last_modified":"Last modified"}, inplace=True)
                df.style.set_properties(align="left")
                # Write to excel with user name and timestamp as filename
                timestamp = datetime.now()
                excel_writer = StyleFrame.ExcelWriter(f'{self.user["name"]}_{timestamp}.xlsx')
                # Style the excel
                sf = StyleFrame(df)
                sf.set_column_width(columns=['Data ID','Data Details','Last modified'],width=40)
                sf.set_column_width(columns=['Data Value'],width=20)
                sf.apply_column_style(cols_to_style=['Data ID','Data Details','Data Value','Last modified'],styler_obj=Styler(horizontal_alignment='left'),style_header=True)
                sf.to_excel(excel_writer=excel_writer)
                # Excel file will be downloaded to the current working directory
                excel_writer.save()
                print("Data downloaded.")

        input('Press any key to continue...')
        return self.switch_menu(activity='action')


