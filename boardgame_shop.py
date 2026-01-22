import authentication as auth
from getpass import getpass
import menu


def browse_by_genres(state):
    print('== Genres ==')
    # Get, print and save all unique genres
    genres = []
    query = ''' SELECT DISTINCT games.genre FROM games ORDER BY genre; '''
    result = state['db'].execute_with_fetchall(query)
    for i in range(len(result)):
        print(f'{i + 1}) {result[i][0]}')
        genres.append(result[i][0])
    genre_choice = input('Pick number (or ENTER to return): ')
    # If empty, return
    if genre_choice is None or genre_choice.strip() == '':
        return
    # If int conversion fails, give feedback and return
    try:
        genre = genres[int(genre_choice) - 1]
    except Exception as e:
        print('Please enter a number! ', e)
        return
    # Get count of total games in genre
    query = '''SELECT count(*) FROM games WHERE games.genre=%s; '''
    games_count = state['db'].execute_with_fetchall(query, [genre])
    # Get game_id, title, designer and price for 2 games at a time
    for offset in range(0, games_count[0][0], 2):
        print(f'== {genre} (showing {offset+1}-'
              f'{offset+2} of {games_count[0][0]}) ==')
        query = ''' SELECT games.game_id, games.title, games.designer,
        games.unit_price FROM games WHERE games.genre=%s LIMIT 2 OFFSET %s; '''
        result = state['db'].execute_with_fetchall(query, [genre, offset])
        # Print all games from query result
        for game_index in range(len(result)):
            for attribute_index in range(len(result[game_index])):
                if attribute_index == 0:  # game_id
                    print(f'- ID {result[game_index][attribute_index]}: ',
                          end='')
                if attribute_index == 1:  # title
                    print(result[game_index][attribute_index], end='')
                if attribute_index == 2:  # designer
                    print(f' by {result[game_index][attribute_index]}', end='')
                if attribute_index == 3:  # unit_price
                    print(f' ${result[game_index][attribute_index]}')
        # Get user input
        user_input = input('Options: enter Game ID to add to cart, '
                           '\'n\' for next, ENTER to return. \n>')
        # If input is empty, go back to member menu
        if user_input is None or user_input.strip() == '':
            break
        # If input is 'n' continue loop without adding
        elif user_input.strip() == 'n':
            continue
        else:  # If input is something that is not 'n'
            game_to_add = ''  # game_id of game to add
            user_input = user_input.upper()
            # If it matches with first game
            if user_input == result[0][0]:
                game_to_add = result[0][0]
            # If it matches with second game
            elif user_input == result[1][0]:
                game_to_add = result[1][0]
            # If no match, give feedback and go back to member menu
            else:
                print('No game with that ID.')
                break
            try:
                quantity = int(input('Quantity: '))
            except Exception as e:
                print('Invalid input, please provide a valid integer. ', e)
                break
            if quantity < 1:
                print('Lowest quantity that can be added is 1.')
                break
            add_to_cart(state['user_id'], game_to_add, quantity)
    return


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
                browse_by_genres(state)
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
