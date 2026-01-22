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
