def print_header():
    print('********************************************')
    print('*** Welcome to the Online Boardgame Shop ***')
    print('********************************************')


def print_main_menu():
    print_header()
    print('1) User Login')
    print('2) New member Registration')
    print('q) Exit')
    return input('\n Type in your choice: ')


def print_store_menu():
    print_header()
    print('Member menu:')
    print('1) Browse by genre')
    print('2) Search by designer/title')
    print('3) View cart')
    print('4) Checkout')
    print('5) Log out')
    return input('\n Type in your choice: ')


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
        return '', 0
    # If int conversion fails, give feedback and return
    try:
        genre = genres[int(genre_choice) - 1]
    except Exception as e:
        print('Please enter a number! ', e)
        return '', 0
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
            # Validate quantity input as positive integer
            quantity = input('Quantity: ')
            if not quantity.isdigit():
                print('Invalid input, please provide a valid integer. ')
                break
            if quantity < 1:
                print('Lowest quantity that can be added is 1.')
                break
    return game_to_add, quantity


def search_for_game(state):
    return
