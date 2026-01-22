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
    # Get, print and save all unique genres
    genres = []
    query = ''' SELECT DISTINCT games.genre FROM games ORDER BY genre; '''
    result = state['db'].execute_with_fetchall(query)
    for i in range(len(result)):
        print(f'{i + 1}) {result[i][0]}')
        genres.append(result[i][0])
    genre_choice = input('Pick number (or ENTER to return): ')
    # If empty, return
    if genre_choice is None or genre_choice.strip == '':
        return
    try:
        genre = genres[int(genre_choice) - 1]
    except Exception as e:
        print('Please enter a number! ', e)
        return
    # Get game_id, title, designer and price for all games in chosen genre
    query = ''' SELECT games.game_id, games.title, games.designer,
    games.unit_price FROM games WHERE games.genre=%s; '''
    result = state['db'].execute_with_fetchall(query, [genre])
    # Print all games from genre
    for i in range(len(result)):
        for z in range(0, 4):
            if z == 0:  # game_id
                print(f'- ID {result[i][z]}: ', end='')
            if z == 1:  # title
                print({result[i][z]}, end='')
            if z == 2:  # designer
                print(f' by {result[i][z]}', end='')
            if z == 3:  # unit_price
                print(f' ${result[i][z]}')
    # SELECT count(*)
    # FROM games
    # WHERE games.genre=%s;

    return
