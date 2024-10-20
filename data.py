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

    def execute_sql(self, argument: str, values:dict|int={}) -> sqlite3.Cursor:
        """ Execute SQL statement on the database.

        Args:
        argument (str): The SQL statement to execute.
        values (dict|int, optional): A dictionary representing the SQL statement values or note id.
        Defaults to None.

        Returns:
        bool: True if the SQL statement executed successfully, False otherwise.

        Raises:
        ValueError: If the provided argument is invalid. """
        if argument not in SQL:
            raise ValueError(f"Invalid SQL argument: {argument}")
        if isinstance(values, int):
            values = {'id': values}  # convert note rowid to dict for sqlite3
        if DEBUG: print(f"INFO : Executing SQL: '{argument}' for note {values.get('id')}")
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