import bcrypt
from database import Database


def authenticate_db(username, password, db_name):
    db = None
    try:
        db = Database(username, password, db_name)
    except Exception as e:
        print('Error connecting to database: ', e)
    return db


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def login(email, password, state):
    state['authenticated'] = True
    return


def create_user(fname, lname, street, city,
                postal_code, phone, email, password, state):
    # Validate inputs
    failed_checks = False
    not_nullable = (fname, lname, street, city, postal_code, email, password)
    for i in range(0, len(not_nullable)):
        if not_nullable[i] is None or not_nullable[i].strip() == '':
            if i == 0:
                print('First name cannot be empty!')
                failed_checks = True
            if i == 1:
                print('Last name cannot be empty!')
                failed_checks = True
            if i == 2:
                print('Street cannot be empty!')
                failed_checks = True
            if i == 3:
                print('City cannot be empty!')
                failed_checks = True
            if i == 4:
                print('Postal code cannot be empty!')
                failed_checks = True
            if i == 5:
                print('Email cannot be empty!')
                failed_checks = True
            if i == 6:
                print('Password cannot be empty!')
                failed_checks = True
    password = hash_password(password)  # Encrypt password
    # Check for duplicate email address
    query = '''SELECT email FROM users WHERE users.email=%s;'''
    result = state['db'].execute_with_fetchall(query, [email])
    if result:
        print(f'A user with email address {email} already exists!')
        failed_checks = True
    # If input validation failed, return without creating user
    if failed_checks is True:
        return
    try:
        # Create user in database
        query = '''INSERT INTO users (first_name, last_name, street, city,
                postal_code, phone_no, email, pwd_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        state['db'].execute_with_commit(query, (fname, lname, street, city,
                                                postal_code, phone,
                                                email, password))
    except Exception as e:
        print(e)
    print('Registration successful. Please login from main menu.')
    return
