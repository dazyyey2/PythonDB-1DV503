from mysql.connector import connect


class Database:
    def __init__(self, username, password, database_name):
        self.connection = connect(host='localhost', user=username,
                                  password=password, database=database_name)

    def get_cursor(self):
        return self.connection.cursor()

    def execute_with_fetchall(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_with_commit(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid  # Return id of created
