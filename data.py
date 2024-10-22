import os
import sqlite3
from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QMessageBox

DEBUG = os.getenv('DEBUG')
SQL = {
    'init': '''CREATE TABLE IF NOT EXISTS notes (
        id      INTEGER     PRIMARY KEY,
        text    TEXT        NOT NULL,
        xpos    INTEGER,
        ypos    INTEGER,
        width   INTEGER,
        height  INTEGER,
        bgcolor TEXT,
        font    TEXT);''',

    'retrieve': 'SELECT * FROM notes;',

    'upsert': '''INSERT INTO notes(id, text, xpos, ypos, width, height, bgcolor, font)
        VALUES(:id, :text, :xpos, :ypos, :width, :height, :bgcolor, :font)
        ON CONFLICT(id) DO UPDATE
        SET text = :text, xpos = :xpos, ypos = :ypos, width = :width, height = :height,
        bgcolor = :bgcolor, font = :font WHERE id = :id;''',

    'update': '''UPDATE notes SET text = :text, xpos = :xpos, ypos = :ypos,
        width = :width, height = :height WHERE id = :id;''',

    'delete': 'DELETE FROM notes WHERE id = :id;',

    'pref_init': '''CREATE TABLE IF NOT EXISTS preferences (
        id      INTEGER     PRIMARY KEY,
        checked INTEGER        NOT NULL,
        bgcolor TEXT,
        font    TEXT,
        fcolor  TEXT);''',

    'pref_insert': '''INSERT INTO preferences(id, checked, bgcolor, font, fcolor)
        VALUES (0, 1, 'lemonchiffon', '', 'black');''',

    'pref_get': 'SELECT checked, bgcolor, font, fcolor FROM preferences WHERE id = 0;',

    'pref_update': '''UPDATE preferences
        SET checked = ?, bgcolor = ?, font = ?, fcolor = ? WHERE id = 0;''',
}

class DataBaseConnector(ABC):
    """ An abstract class for note-storing functionality. """
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """ Open a database connection. """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> list:
        """ Return a list of all notes in the database. """
        raise NotImplementedError

    @abstractmethod
    def save(self, note: dict) -> bool:
        """ Save a note in the database.

        Args:
            note (dict): Database record of note as a dictionary.

        Returns:
            bool: True if note saved successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def update(self, note: dict) -> bool:
        """ Update a note in the database.

        Args:
            note (dict): Database record of note as a dictionary.

        Returns:
            bool: True if note saved successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def delete(self, rowid: int) -> bool:
        """ Delete a note from the database.

        Args:
            rowid (int): The ID of the note.

        Returns:
            bool: True if note deleted successfully, False otherwise. """
        raise NotImplementedError


class SQLiteConnector(DataBaseConnector):
    """ A SQLite3 connector. """
    def __init__(self, db:str) -> None:
        """ Initialize the database connection.

        Args:
            db (str): The path of the SQLite database file. """
        self.conn = sqlite3.connect(db)
        self.execute_sql('init')
        self.execute_sql('pref_init')
        if not self.execute_sql('pref_get').fetchone():
            self.execute_sql('pref_insert')

    def execute_sql(self, argument: str, values:dict|tuple|int={}) -> sqlite3.Cursor|None:
        """ Execute SQL statement on the database.

        Args:
            argument (str): The SQL statement to execute.
            values (dict|tuple|int, optional): A dictionary representing the SQL statement values or note id.
                Defaults to None.

        Returns:
            sqlite3.Cursor: The cursor object with SQL query result.

        Raises:
            ValueError: If the provided argument is invalid. """
        if argument not in SQL:
            raise ValueError(f"Invalid SQL argument: {argument}")
        if isinstance(values, int):
            values = {'id': values}  # convert note rowid to dict for sqlite3
        if DEBUG: print(f"INFO : Executing SQL: '{argument}' with {values.get('id') if isinstance(values, dict) else values}")
        try:
            cursor = self.conn.execute(SQL[argument], values)
            self.conn.commit()
        except sqlite3.Error as e:
            if DEBUG: print(f"ERROR: Executing SQL '{argument}' statement: {e}")
            QMessageBox.critical(None, "Error", f"Error ocurred while executing SQL '{argument}' statement: {e}")
            return None
        return cursor

    def retrieve(self) -> list:
        """ Return a list of all notes in the database.

        Returns:
            list: A list of tuples representing notes. """
        return self.execute_sql('retrieve').fetchall()

    def save(self, note: dict) -> bool:
        """ Save a note in the database. """
        return bool(self.execute_sql('upsert', note))

    def update(self, note: dict) -> bool:
        """ Update a note in the database. """
        return bool(self.execute_sql('update', note))

    def delete(self, rowid: int) -> bool:
        """ Delete a note from the database. """
        return bool(self.execute_sql('delete', rowid))

    def get_preferences(self) -> tuple:
        """ Retrieve the application preferences.

        Returns:
            tuple: A tuple containing the checked state, background color, and font. """
        return self.execute_sql('pref_get').fetchone()

    def save_preferences(self, preferences:tuple) -> bool:
        """ Save the global preferences in database.

        Args:
            preferences (tuple): A tuple containing the checked state background color and font"""
        return bool(self.execute_sql('pref_update', preferences))