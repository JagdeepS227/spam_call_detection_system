
                                            SPAM CHECK APP

Incase of any query feel free to reach out to:
Jagdeep Singh
jagdeep2620@gmail.com




Assumptions:
1) When a phone number is searched the result will come,
        if it is registered as any user,
        OR contact of any user,
        OR it is reported spam by any user.

2) I have allowed to set phone numbers of 10 digits only, it can be
    changed by constant PHONE_NUMBER_LENGTH in file spam_check/constants.py

3) A number can be marked spam once only by an user.

4) User's phone number is used to login along with password.

5) There are 6 endpoints for this app:
    creating a new user : POST  http://127.0.0.1:8000/auth/users/
    log in : POST http://127.0.0.1:8000/auth/token/login/
    Creating a contact: POST http://127.0.0.1:8000/api/contacts/
    Listing all contacts of logged in user: GET http://127.0.0.1:8000/api/contacts/
    Reporting a phone number as spam: POST http://127.0.0.1:8000/api/report-spam/
    Searching a phone number or name: GET localhost:8000/api/search/?q=<name(partial or full)/phone number>

    More detailed usage is described in the end of this document




This submission includes following surplus points:
1) Pagination ( currently set at 1000 search results per page, as it makes sense once integrated with UI )
2) API rate limiting ( currently limiting to 2000/ min requests by a single user )
3) Database indexing ( to have faster db queries from tables where we going through users or picking a number from table)
4) Unit tests ( some basic unit tests to ensure basic functionalities work as expected ) at spam_check/tests/ directory.
                python manage.py test spam_check.tests

5) Each endpoint( except registering new user) is accessible only with an Authorization token.
6) A script to seed dta into database, to test on scale. Feel free to adjust data seeding volume from seed_data.py file in spam_check/management/commands/ directory.
                python manage.py seed_data
                data seeding logs can be seen in file Data_writing_logs.txt, all users will be created with password Test@123

7) Used Djoser package of Django to setup User registration and login, it by default uses PBKDF2 with SHA256 for encrypting passwords.
8) Used Faker to generate data to seed into database.
9) When a number or name is searched, each result contains number of times that number associated with each result is marked or reported as spam along with
    how much likelihood of this number or result of being spam is:
    "Not spam" if not reported by anyone as spam
    "Low" if reported by less than 3 users
    "Medium" if reported by less than 6 users
    "High" if reported by more than 5 users

10) Passwords need to be of atleast length 8, having each one uppercase and lowercase letter, 1 digit and 1 symbol atleast
11) phone number must be of 10 digits, emails are optional while creating user






                                    ********************************
                                    ********* STEPS TO RUN *********
                                    ********************************


#### I have used mysql database considering high scaling, if one wants to use sqlite or any other db feel free to change in settings.py

#### After activating virtual environment feel free to run following command to install packages required

        pip install requirements.txt

        main packages installed: django, djangorestframework, djoser, Faker, PyMySQL


#### Mysql commands to create database ( same db details set in settings.py )

        CREATE DATABASE spamcheckdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER 'spamuser'@'localhost' IDENTIFIED BY 'Spam@1234';
        GRANT ALL ON *.* TO 'spamuser'@'localhost' WITH GRANT OPTION;
        FLUSH PRIVILEGES;
        EXIT;

#### Django migration related commands:

        python manage.py showmigrations
        python manage.py makemigrations
        python manage.py migrate

#### Django command to run backend server

        python manage.py runserver


##### Django create super user to use admin page

        python manage.py createsuperuser

#### Command to seed data into database using APIs

        python manage.py seed_data

#### Command to run basic unit tests, which creates user, contacts, reports spam and searches

        python manage.py test spam_check.tests









Given below are some examples of how to access different APIs:



##################################################
Creating new user:
POST
http://127.0.0.1:8000/auth/users/
{
  "phone_number": "9876543220",
  "name": "Jagdeep",
  "password": "Strong@123",
  "re_password": "Strong@123"
}


################################################
Logging in existing User
POST
http://127.0.0.1:8000/auth/token/login/
{
  "phone_number": "9876543210",
  "password": "Strong@123"
}

This will return Authorization token as response!


################################################
Creating contacts
POST
http://127.0.0.1:8000/api/contacts/
Authorisation: Token <token value you get after login>
{
  "name": "Dileep Sharma",
  "phone_number": "9876555210"
}


Listing all Contacts:
GET
http://127.0.0.1:8000/api/contacts/
Authorisation: Token <token value you get after login>



##############################################
Reporting a number as spam

POST
http://127.0.0.1:8000/api/report-spam/
Authorisation: Token <token value you get after login>

##############################################

Searching for a number or name

GET
localhost:8000/api/search/?q=<name(partial or full)/phone number>
Authorisation: Token <token value you get after login>

This returns paginated(only if searched with name) results of matches, where each of results contains info like following:
{
    "name": "Jonathan Clark",
    "phone_number": "6529280088",
    "email": null,
    "spam_count": 3,
    "spam_likelihood": "Medium"
}