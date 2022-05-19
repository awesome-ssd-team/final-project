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
