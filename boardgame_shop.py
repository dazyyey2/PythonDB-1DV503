import authentication as auth
from getpass import getpass
import menu


def handle_choices(choice, state):
    # Pre authentication choices
    if state['authenticated'] is False:
        match choice:
            # User Login
            case '1':
                print('== Welcome to the Online Boardgame Shop ==')
                print('== User Login ==')
                email = input('Enter email: ')
                password = getpass('Enter password: ')
                auth.login(email, password, state)
                return False
            # User registration
            case '2':
                print('== Welcome to the Online Boardgame Shop ==')
                print('== New member registration ==')
                fname = input('Enter first name: ')
                lname = input('Enter last name: ')
                street = input('Enter street: ')
                city = input('Enter city: ')
                postal_code = input('Enter postal code: ')
                phone = input('Enter phone (optional): ')
                email = input('Enter email address: ')
                password = getpass('Enter password: ')
                auth.create_user(fname, lname, street, city,
                                 postal_code, phone, email, password, state)
                return False
            case 'q':
                return True  # Exit program loop
            case _:
                print('Invalid input, please enter a valid choice.')
    
    return False


def get_database():
    print('----------------------------------')
    print('Please enter database credentials')
    print('----------------------------------')
    # Establish database connection
    while state['db'] is None:
        state['db'] = auth.authenticate_db(
            input('Username: '),
            getpass('Password: '),
            db_name='boardgame_shop')
    return


if __name__ == '__main__':
    state = {}
    state['db'] = None
    state['authenticated'] = False
    state['user_id'] = None
    # Establish database connection
    get_database()
    # Main program loop
    exit_boolean = False
    while exit_boolean is False:
        # Pre authentication login menu
        if state['authenticated'] is False:
            choice = menu.print_main_menu()  # Get user choice from menu
            exit_boolean = handle_choices(choice, state)
        # Post authentication store menu
        elif state['authenticated'] is True:
            choice = menu.print_store_menu()  # Get user choice from menu
            exit_boolean = handle_choices(choice, state)
