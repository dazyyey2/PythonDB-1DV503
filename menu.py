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


def paginate_games(state, total_count, query, query_params,
                   header, games_per_page):
    game_to_add = ''
    quantity = 0
    # Paginate through games
    for offset in range(0, total_count, games_per_page):
        print(f'== {header} (showing {offset+1}-'
              f'{min(offset+games_per_page, total_count)} of '
              f'{total_count}) ==')
        # Add limit and offset to query
        limited_query = query + f' LIMIT {games_per_page} OFFSET %s;'
        result = state['db'].execute_with_fetchall(
            limited_query, query_params + [offset]
        )
        # Display games
        for game_index in range(len(result)):
            game_id = result[game_index][0]
            title = result[game_index][1]
            designer = result[game_index][2]
            unit_price = result[game_index][3]
            print(f'- ID {game_id}: {title} by {designer} ${unit_price}')
        # Get user input
        user_input = input('Options: enter Game ID to add to cart, '
                           '\'n\' for next, ENTER to return. \n>')
        # If input is empty, return to menu
        if user_input is None or user_input.strip() == '':
            return '', 0
        # If 'n', continue to next page
        elif user_input.strip().lower() == 'n':
            continue
        # User entered a game ID
        else:
            user_input = user_input.upper()
            game_to_add = ''
            # Check if input matches any displayed game
            for game in result:
                if user_input == game[0]:
                    game_to_add = game[0]
                    break
            # If no match found
            if game_to_add == '':
                print('No game with that ID.')
                return '', 0
            # Validate quantity
            quantity = input('Quantity: ')
            if not quantity.isdigit():
                print('Invalid input, please input a valid positive integer.')
                return '', 0
            if int(quantity) < 1:
                print('Lowest quantity that can be added is 1.')
                return '', 0
            return game_to_add, int(quantity)
    # User went through all pages without selecting
    return '', 0


def browse_by_genres(state):
    print('== Genres ==')
    # Get and display all unique genres
    genres = []
    query = 'SELECT DISTINCT games.genre FROM games ORDER BY genre;'
    result = state['db'].execute_with_fetchall(query)
    for i in range(len(result)):
        print(f'{i + 1}) {result[i][0]}')
        genres.append(result[i][0])
    genre_choice = input('Pick number (or ENTER to return): ')
    # If empty, return
    if genre_choice is None or genre_choice.strip() == '':
        return '', 0
    # Validate genre selection
    try:
        genre = genres[int(genre_choice) - 1]
    except Exception as e:
        print('Please enter a number! ', e)
        return '', 0
    # Get total count for this genre
    query = 'SELECT count(*) FROM games WHERE games.genre=%s;'
    games_count = state['db'].execute_with_fetchall(query, [genre])
    total = games_count[0][0]
    # Base query for pagination
    query = '''SELECT games.game_id, games.title, games.designer,
                    games.unit_price FROM games WHERE games.genre=%s'''
    return paginate_games(state, total, query, [genre], genre, 2)


def search_for_game(state):
    # Print options
    print('== Search ==')
    print('1) Search by designer (starts with)')
    print('2) Search by title (whole word)')
    print('3) Back')
    user_input = input('Type in your choice: ')
    match user_input:
        # Search by designer
        case '1':
            designer_input = input('Designer starts with: ')
            query = ('SELECT count(*) FROM games '
                     'WHERE games.designer LIKE %s;')
            result = state['db'].execute_with_fetchall(
                query, [designer_input + '%']
            )
            games_count = result[0][0]
            if games_count == 0:
                print(f'No designers that starts with '
                      f'{designer_input} found')
                return '', 0
            query = ('SELECT games.game_id, games.title, '
                     'games.designer, games.unit_price '
                     'FROM games WHERE games.designer LIKE %s')
            header = (f'Games from designers that starts with '
                      f'{designer_input}')
            return paginate_games(
                state, games_count, query,
                [designer_input + '%'], header, 3)
        # Search by title
        case '2':
            # SELECT count(*) FROM games WHERE games.title LIKE "%CITY%"
            # SELECT games.title FROM games WHERE games.title LIKE "%CITY%"
            title_input = input('Title contains word: ')
            query = ('SELECT count(*) FROM games '
                     'WHERE games.title LIKE %s;')
            result = state['db'].execute_with_fetchall(
                query, ['%' + title_input + '%']
            )
            games_count = result[0][0]
            if games_count == 0:
                print(f'No games that contains '
                      f'{title_input} found')
                return '', 0
            query = ('SELECT games.game_id, games.title, '
                     'games.designer, games.unit_price '
                     'FROM games WHERE games.title LIKE %s')
            header = (f'Games that contain the word {title_input}')
            return paginate_games(state, games_count, query,
                                  ['%' + title_input + '%'], header, 3)
        # Go back
        case '3':
            return '', 0
        case _:
            print('Please enter a valid input')
            return '', 0
