import bcrypt
from database import Database


def authenticate_db(username, password, db_name):
    db = None
    try:
        db = Database(username, password, db_name)
    except Exception as e:
        print('Error connecting to database: ', e)
    return db


# Hash and salt password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def login(email, password, state):
    # Check for empty inputs
    if email is None or email.strip() == '':
        print('Email cannot be empty!')
        return
    if password is None or password.strip() == '':
        print('Password cannot be empty!')
        return
    # Get password hash from database
    query = '''SELECT pwd_hash FROM users WHERE users.email=%s;'''
    result = state['db'].execute_with_fetchall(query, [email])
    # If no results, no user with that email exists
    if not result:
        print(f'No user with email address {email}')
        return
    hashed_password = result[0][0]
    # Compare the hashed password from database to given password
    if bcrypt.checkpw(password.encode('utf-8'),
                      hashed_password.encode('utf-8')):
        # After successful authentication, save user_id
        query = '''SELECT user_id FROM users WHERE users.email=%s;'''
        user_id = state['db'].execute_with_fetchall(query, [email])
        state['user_id'] = user_id[0][0]
        # Switch authenticated flag
        state['authenticated'] = True
        print('Successfully authenticated!')
    else:
        print('Incorrect password, please try again.')
    return


# Validate user input and create new user in database
def create_user(fname, lname, street, city,
                postal_code, phone, email, password, state):
    failed_checks = False
    not_nullable = (fname, lname, street, city, postal_code, email, password)
    # Validate all inputs that cannot be empty
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
    password = hash_password(password)  # Hash and salt password
    # Check if email address already exists in database
    query = '''SELECT email FROM users WHERE users.email=%s;'''
    result = state['db'].execute_with_fetchall(query, [email])
    if result:
        print(f'A user with email address {email} already exists!')
        failed_checks = True
    # If input validation failed, return without creating user
    if failed_checks is True:
        return
    try:
        # If input validation is successful, create user in database
        query = '''INSERT INTO users (first_name, last_name, street, city,
                postal_code, phone_no, email, pwd_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        state['db'].execute_with_commit(query, (fname, lname, street, city,
                                                postal_code, phone,
                                                email, password))
    except Exception as e:
        print('Error creating user: ', e)
        return
    print('Registration successful. Please login from main menu.')
    return
