from mysql.connector import connect


class Database:
    def __init__(self, username, password, database_name):
        self.connection = connect(host='localhost', user=username,
                                  password=password, database=database_name)
