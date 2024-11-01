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
            return
        try:
            with self._connectDB() as connection:
                cursor = connection.cursor()
                cursor.execute(query, args)
                connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

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

# Define SQL statements for creating tables

create_game_table = """
CREATE TABLE IF NOT EXISTS Game (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    game_status TEXT CHECK(game_status IN ('voting', 'drawing', 'guessing', 'completed')) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    side_prompt_guessed_count INTEGER DEFAULT 0
);
"""

create_player_table = """
CREATE TABLE IF NOT EXISTS Player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('guesser', 'drawer')) NOT NULL
    game_id INTEGER,
    score INTEGER DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

create_vote_table = """
CREATE TABLE IF NOT EXISTS Vote (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    theme_choice TEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

create_prompt_table = """
CREATE TABLE IF NOT EXISTS Prompt (
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    main_prompt TEXT NOT NULL,
    side_prompt TEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

create_drawing_table = """
CREATE TABLE IF NOT EXISTS Drawing (
    drawing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    drawing_data BLOB NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

create_guesses_table = """
CREATE TABLE IF NOT EXISTS Guesses (
    guess_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    guess_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    guessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

create_round_score_table = """
CREATE TABLE IF NOT EXISTS RoundScore (
    round_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Player (player_id),
    FOREIGN KEY (game_id) REFERENCES Game (game_id)
);
"""

db = DB('game_database.db')

# Create tables
db.create_table(create_game_table)
db.create_table(create_player_table)
db.create_table(create_vote_table)
db.create_table(create_prompt_table)
db.create_table(create_drawing_table)
db.create_table(create_guesses_table)
db.create_table(create_round_score_table)