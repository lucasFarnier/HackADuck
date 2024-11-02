import sqlite3

class DB:
    def __init__(self, fileName):
        self.__fileName = fileName

    def _connectDB(self):
        return sqlite3.connect(self.__fileName)
    
    def select(self, query, args=None):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                if args:
                    cursor.execute(query,args)
                else:
                    cursor.execute(query)
                records = cursor.fetchall()
                return records
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def insert(self, query, args):
        if args is None:
            print("Args can not be type None")
            return False
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def insertAndFetch(self, query, args=None):
        if args is None:
            print("Args can not be type None")
            return None
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
                cursor.execute("SELECT last_insert_rowid()")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def delete(self, query, args):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def update(self, query, args=None):
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                if args:
                    cursor.execute(query,args)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def create_table(self, create_table_sql):
        """Creates a new table in the database."""
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(create_table_sql)
                connection.commit()
                print("Table created successfully")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")