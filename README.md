# Secure Software Development (Computer Science) - Development Team Project

## Quick Start

1. Clone the repo

```
$ git clone https://github.com/awesome-ssd-team/final-project.git
$ cd final-project
```

2. Initialize and activate a virtualenv:

```
$ virtualenv --no-site-packages env
$ source env/bin/activate
```

3. Install the dependencies:

```
$ pip install -r requirements.txt
```

4. Setup the environment configuration

```
cp .env.example .env
```

5. Update the values for the .env file

6. Run the development client application:

```
$ dotenv run -- python main.py
```

7. The main menu will be shown on the terminal window

8. Run test

```
$ tox -e all
```

## Introduction

This is a command line application that allows user to register, login, and perform CRUD operations. Admin users can retrieve user logs and manage users.

## Scenario

Due to the global Covid Pandemic, cyber attacks have increased dramatically. CERN has contacted us to develop a microservice application to address concerns of scalability
and security. The application should:

- Perform secure CRUD operations
- Emphasis on security best practises
- Command Line application
- GDPR Compliant

## Architecture

The application is a command line application built in python. It makes use of Cloud Functions by Google Cloud Platform to handle the API calls and execute CRUD operations to the MYSQL databases hosted in AWS Relational Database Service (RDS).

## Functions

### Register a new user

As the application is started, the user can select to get registered. The application will ask the use to set the first and second passwords, as well as MFA. It is recommended for the user to set up MFA to enhance security. User can use OTP applications such as Google Authenticator to scan the QR coode displayed and entered the MFA code. If it is successful, the OTP secret will be saved to the user database for future authentication purpose.

### Login

After registering, the user can login using the registered email address. The user will be prompted to set up MFA if not yet done so. Otherwise, after the correct password and MFA code have been entered, the login is successful and the user will be directed to the main page. For incorrect login credentials, user will be blocked temporarily for 15 minutes if there are more than 3 unsuccessful login attempts. This feature is to prevent the brute force attack.

### User main menu

In user main menu, the user can choose to add, update, delete or download the data, or to logout. The valid data entered by the user will be displayed on this page.

#### Adding data

User can perform addition of data into the database. The user only has to input the data value and data details. The data id will be automatically generated and the data is set to be valid by default.

#### Updating data

User can choose to either update the data value or the data details of a valid data at each time. The values will be updated to the database.

#### Deleting data

User can delete the data by entering the data ID. However, due to data concerns (eg. accidental deletion), the deletion action is only marking the data as invalid but not actual deletion. The data will still be accessible in the database if needed.

#### Downloading data

User can select this option to download a copy of his/her valid data. The data will be exported in an excel format and downloaded to the current working directory. If no valid data is present, it will prompt the user there is no data to be downloaded and direct the user back to the main menu.

#### Logout

When user selects to logout, the application will clear the user information stored for the session and direct the user back to the login/register screen.

## Administrator features

The application also provides administrator features that allow administrators to monitor user activities and mange user privileges.
Other than the above features which are available for the regular users, the admin user has two more features listed below:

### Manage users

Administrtors can view user details and manage their roles in the admin portal. 

Once clicking into the Manage User page, a list of existing users will show.Some of the user's details (email and full_name) are encrypted.
The admin can manage the user by:
  - Activate/deactivate a user
  - Update a regulare user as an admin user

### View user logs

Administrators can view and monitor and user activities in the application. It is important to have enough logs and monitoring to detect suspicious activities.
With the logs feature, the admin can:
 - Monitor the activities' time to identify the suspicious activity. For example, if the data is being download after the working hours, the activity could be considered as suspicious.
 - Monitor if a specific user has unusual behavior. For example, if huge amount of data is suddenly deleted by a specific user, then we can confirm with the user if the activities are expected.

## Steps forwards

Due to several constraints, the application is developed in a command line interface. In future steps, it should be considered to develop a web interface as well for better user navigation and user experience.
