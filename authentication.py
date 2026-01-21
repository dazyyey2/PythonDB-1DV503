# import hashlib
from database import Database


def authenticate_db(username, password, db_name):
    db = None
    try:
        db = Database(username, password, db_name)
    except Exception as e:
        print('Error connecting to database: ', e)
    return db


if __name__ == '__main__':
    print('hello world!')
