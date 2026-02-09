from datetime import date, timedelta


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


# Print current cart
def view_cart(state):
    total = 0
    print('------------------------------------------------------------------')
    print('Game ID     Title                            $      Qty     Total')
    print('------------------------------------------------------------------')
    query = '''SELECT games.game_id,games.title,games.unit_price,cart.quantity
    FROM games
    JOIN cart ON cart.game_id=games.game_id
    WHERE cart.user_id=%s;'''
    result = state['db'].execute_with_fetchall(query, [state['user_id']])
    for game_index in range(len(result)):
        game_id = result[game_index][0]
        title = result[game_index][1]
        unit_price = result[game_index][2]
        quantity = result[game_index][3]
        # If title is longer than 30 characters, cut it off and add ".."
        if len(title) > 30:
            title = title[:30] + '..'
        else:
            # If it is shorter than 30, add missing spaces (32 because of "..")
            title = title + ' ' * (32 - len(title))
        line_total = unit_price * quantity
        total += line_total
        print(f'{game_id}    {title} {unit_price}   {quantity}   {line_total}')
    print('------------------------------------------------------------------')
    print(f'\nTotal = ${total}\n')
    input('Press Enter to return to the main menu')
    return


# Print current cart / checkout
def checkout(state):
    # Print current cart
    total = 0
    print('------------------------------------------------------------------')
    print('Game ID     Title                            $      Qty     Total')
    print('------------------------------------------------------------------')
    query = '''SELECT games.game_id,games.title, games.unit_price,cart.quantity
    FROM games
    JOIN cart ON cart.game_id=games.game_id
    WHERE cart.user_id=%s;'''
    result = state['db'].execute_with_fetchall(query, [state['user_id']])
    for game_index in range(len(result)):
        game_id = result[game_index][0]
        title = result[game_index][1]
        unit_price = result[game_index][2]
        quantity = result[game_index][3]
        # If title is longer than 30 characters, cut it off and add ".."
        if len(title) > 30:
            title = title[:30] + '..'
        else:
            # If it is shorter than 30, add missing spaces (32 because of "..")
            title = title + ' ' * (32 - len(title))
        line_total = unit_price * quantity
        total += line_total
        print(f'{game_id}    {title} {unit_price}   {quantity}   {line_total}')
    print('------------------------------------------------------------------')
    print(f'\nTotal = ${total}\n')
    user_input = input('Proceed to checkout (Y/N)? ')
    # If user doesn't want to go to checkout, return to menu
    if user_input.upper() != 'Y':
        return
    # Checkout
    # Get user information
    query = '''SELECT street, city, postal_code, first_name, last_name
     FROM users WHERE user_id=%s'''
    result = state['db'].execute_with_fetchall(query, [state['user_id']])
    street = result[0][0]
    city = result[0][1]
    postal_code = result[0][2]
    first_name = result[0][3]
    last_name = result[0][4]
    order_date = date.today()
    # Create order
    query = '''INSERT INTO orders (user_id,created,ship_street,ship_city,ship_postal_code)
    VALUES (%s, %s, %s, %s, %s)'''
    order_no = state['db'].execute_with_commit(query, [state['user_id'], order_date, street, city, postal_code])
    # Create order_items
    query = '''SELECT cart.game_id,cart.quantity,games.unit_price
    FROM cart
    JOIN games ON games.game_id=cart.game_id
    WHERE cart.user_id=%s;'''
    result = state['db'].execute_with_fetchall(query, [state['user_id']])
    # Add all games from cart to order_items with order_no from new order
    for i in range(len(result)):
        game_id = result[i][0]
        quantity = result[i][1]
        price = result[i][2]
        line_total = price * quantity
        query = '''INSERT INTO order_items (order_no,game_id,quantity,line_total)
        VALUES (%s, %s, %s, %s)'''
        state['db'].execute_with_commit(query, [order_no, game_id, quantity, line_total])
    # Delete the cart
    query = 'DELETE FROM cart WHERE user_id=%s'
    state['db'].execute_with_commit(query, [state['user_id']])
    # Display invoice
    print('==============================================================')
    print(f'Invoice for Order no. {order_no}')
    print('==============================================================\n')
    print(f'Name: {first_name} {last_name}')
    print(f'Address: {street}, {city}')
    print(f'Postcode: {postal_code}')
    # Get estimated delivery date
    estimated_delivery = order_date + timedelta(days=7)
    print(f'Estimated delivery: {estimated_delivery}')
    print('--------------------------------------------------------------')
    print('Game ID     Title                            $      Qty     Total')
    print('--------------------------------------------------------------')
    query = '''SELECT order_items.game_id,order_items.quantity,order_items.line_total,
    games.title, games.unit_price
    FROM order_items
    JOIN games ON games.game_id=order_items.game_id
    WHERE order_items.order_no=%s;'''
    result = state['db'].execute_with_fetchall(query, [order_no])
    for game_index in range(len(result)):
        game_id = result[game_index][0]
        title = result[game_index][3]
        unit_price = result[game_index][4]
        quantity = result[game_index][1]
        line_total = result[game_index][2]
        # If title is longer than 30 characters, cut it off and add ".."
        if len(title) > 30:
            title = title[:30] + '..'
        else:
            # If it is shorter than 30, add missing spaces (32 because of "..")
            title = title + ' ' * (32 - len(title))
        print(f'{game_id}    {title} {unit_price}   {quantity}   {line_total}')
    print('--------------------------------------------------------------')
    print(f'\nTotal = ${total}\n')
    print('==============================================================')
    input('Press Enter to return to the main menu')
    return
