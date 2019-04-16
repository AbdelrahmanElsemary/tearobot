"""
    Database management module
"""
import os
import sqlite3

from sqlite3 import Error
from .data_types import User
from . import BASE_DIR

DB_FILE = BASE_DIR / 'db' / 'bot.db'
DB_SQL_SCRIPT = BASE_DIR / 'db' / 'bot.db.sql'


class DBHelper():

    def __init__(self, filename=DB_FILE):
        try:
            self.conn = sqlite3.connect(filename)  # new db connection
            self.cur = self.conn.cursor()  # obtain a cursor
        except Error as err:
            exit(err)

    def __del__(self):
        """On object destruction"""
        self.conn.close()

    def setup(self) -> bool:
        """Set up database for dev/test purpose or for first time use"""
        try:
            self.conn.executescript(DB_SQL_SCRIPT)
            print("DB setup was successful")
        except Error as err:
            exit(err)
        return True

    def destroy(self):
        try:
            self.conn.execute("DROP TABLE User;")
            self.conn.execute("DROP TABLE Message;")
            self.conn.commit()
            print("dropping tables... done.")
            self.conn.close()
            os.remove(path="../db/dev.db")
            print("removed db file")
        except Error as err:
            exit(err)

    def query(self, sql: str, params: tuple):
        """Executes a custom query"""
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
        except Error as err:
            self.conn.rollback()
            exit(err)

    def add_message(self, params: tuple) -> bool:
        """Insert a new Message

        ``params`` tuple: id, update_id, user_id, chat_id, date, text"""
        sql = "INSERT INTO Message VALUES (?, ?, ?, ?, ?, ?)"
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
            return True
        except Error as err:
            self.conn.rollback()
            exit(err)

    def get_messages(self, user_id=None) -> list:
        """Retrieve messages for a certain user"""
        sql = "SELECT * FROM Message WHERE user_id = ?"
        try:
            result = self.cur.execute(sql, user_id)
            rows = [row for row in result]
        except Error as err:
            exit(err)
        return rows

    def add_user(self, params: tuple) -> bool:
        """Insert a new user

        ``params`` (id, is_bot, is_admin, first_name, last_name, username, language_code, active, created,
        updated, last_command)"""
        sql = "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            self.cur.execute(sql, params)
            self.conn.commit()
            return True
        except Error as err:
            self.conn.rollback()
            exit(err)

    def get_user(self, user_id: int) -> tuple:
        """Get a user object using ``user_id``"""
        try:
            result = self.cur.execute("SELECT * FROM User WHERE id = ?", user_id)
            user = User(*result.fetchone())
        except Error as err:
            exit(err)
        return user

    def get_user_last_command(self, user_id: int) -> str:
        pass

    def set_user_last_command(self, user_id: int, updated: int, last_command: str):
        """Update user's last command"""
        try:
            sql = "UPDATE User SET updated = ?, last_command = ? WHERE user_id = ?"
            self.cur.execute(sql, (updated, last_command, user_id))
            self.conn.commit()
            return True
        except Error as err:
            self.conn.rollback()
            exit(err)

    def get_user_status(self, user_id: int) -> int:
        pass

    def set_user_status(self, user_id: int, updated: int, active: bool):
        """Activate/deactivate a user"""
        status = 0
        if active:
            status = 1
        try:
            sql = "UPDATE User SET updated = ?, active = ? WHERE user_id = ?"
            self.cur.execute(sql, (updated, status, user_id))
            self.conn.commit()
            return True
        except Error as err:
            self.conn.rollback()
            exit(err)
