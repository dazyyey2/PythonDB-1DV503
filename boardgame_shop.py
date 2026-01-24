import authentication as auth
from getpass import getpass
import menu


def add_to_cart(user_id, game_id, quantity):
    # Find current quantity of game in cart
    query = (''' SELECT cart.quantity FROM cart '''
             '''WHERE cart.user_id=%s AND cart.game_id=%s; ''')
    previous_cart_quantity = state['db'].execute_with_fetchall(
        query, [user_id, game_id]
    )
    # If the game is already in cart, add the new quantity to it
    if len(previous_cart_quantity) > 0:
        query = (''' UPDATE cart SET quantity=quantity+%s '''
                 ''' WHERE user_id=%s AND game_id=%s; ''')
        state['db'].execute_with_commit(query, [quantity, user_id, game_id])
    else:  # If game is not already in cart, insert it with quantity
        query = (''' INSERT cart(user_id, game_id, quantity) '''
                 ''' VALUES (%s, %s, %s) ''')
        state['db'].execute_with_commit(query, [user_id, game_id, quantity])
    print('Added to cart.')
    return


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
            case 'q':
                return True  # Exit program loop
            case _:
                print('Invalid input, please enter a valid choice.')
    # Post authentication choices
    elif state['authenticated'] is True:
        match choice:
            # Browse by genre
            case '1':
                game_id, quantity = menu.browse_by_genres(state)
                if (game_id.strip() != '' and quantity != 0
                        and quantity is not None):
                    add_to_cart(state['user_id'], game_id, quantity)
            # Search by designer/title
            case '2':
                return
            # View cart
            case '3':
                return
            # Checkout
            case '4':
                return
            # Log out
            case '5':
                state['authenticated'] = False
                state['user_id'] = None
            case _:
                print('Invalid input, please enter a valid choice.')
    return False  # Continue program loop


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
