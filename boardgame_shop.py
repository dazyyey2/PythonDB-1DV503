import authentication as auth
from getpass import getpass
import menu

if __name__ == '__main__':
    state = {}
    state['db'] = None
    while state['db'] is None:
        state['db'] = auth.authenticate_db(
            input('Enter database username: '),
            getpass('Enter database password: '),
            db_name='boardgame_shop')
    choice = menu.print_login_menu()
