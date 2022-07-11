import sqlite3
import pickle
import os

class MetaSingleton(type):
  """
  Class represents Sinfleton-pattern for database
  """
  _instances = {}

  def __call__(cls, *args, **kwargs):
      if cls not in cls._instances:
          cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
      return cls._instances[cls]


class ContractsDatabase(metaclass=MetaSingleton):
    def __init__(self, path=""):
        db_filepath = path + "contracts.db"

        if not os.path.exists(db_filepath):
          open(db_filepath, 'a').close()

        if path == "":
            self.conn = sqlite3.connect(db_filepath, check_same_thread=False)
        else:
            self.conn = sqlite3.connect(db_filepath, check_same_thread=False)

        self.cur = self.conn.cursor()
        # self.cur.execute("DROP TABLE IF EXISTS users;")
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY NOT NULL,
            uid BIG INT,
            privateKey TEXT);''')
        self.conn.commit()

        # self.cur.execute("DROP TABLE IF EXISTS contracts;")
        self.cur.execute('''CREATE TABLE IF NOT EXISTS contracts
            (id INTEGER PRIMARY KEY NOT NULL,
            address TEXT);''')
        self.conn.commit()

    def insert_contract(self, contractAddress):
        try:
            sqlite_insert_query = 'INSERT INTO contracts(address) VALUES (?)'
            self.cur.execute(sqlite_insert_query, (contractAddress,))
            self.conn.commit()
            return contractAddress
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def insert_new_user(self, uid, privateKey):
        try:
            sqlite_insert_query = 'INSERT INTO users(uid, privateKey) VALUES (?, ?)'
            self.cur.execute(sqlite_insert_query, (uid, privateKey))
            self.conn.commit()
            return uid
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def get_all_contracts(self):
        try:
            sqlite_select_query = 'SELECT address FROM contracts'
            answer = self.cur.execute(sqlite_select_query,()).fetchall()
            if answer is None:
                return None
            else:
                return [addr[0] for addr in answer]
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def get_last_contract(self):
        try:
            sqlite_select_query = 'SELECT address FROM contracts'
            answer = self.cur.execute(sqlite_select_query,()).fetchone()
            if answer is None:
                return None
            else:
                return answer[0]
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def get_user_by_uid(self, uid):
        try:
            sqlite_select_query = 'SELECT privateKey FROM users WHERE uid == ?'
            answer = self.cur.execute(sqlite_select_query, (uid,)).fetchone()
            if answer is None:
                return None
            else:
                return answer[0]
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def update_user_key(self, uid, new_key):
        try:
            sqlite_select_query = 'UPDATE users set privateKey = ? WHERE uid == ?'
            self.cur.execute(sqlite_select_query, (new_key, uid))
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)

    def __del__(self):
        self.cur.close()
        self.conn.close()
        print('Database connection closed')
