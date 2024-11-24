import sqlite3
import logging

from qsticky.data.abstract import DataBaseConnector, HandleError

logger = logging.getLogger(__package__)

class SQLiteConnector(DataBaseConnector):
    """ A SQLite3 connector. """
    SQL = {
        'init': '''CREATE TABLE IF NOT EXISTS notes (
            id      INTEGER     PRIMARY KEY,
            text    TEXT        NOT NULL,
            xpos    INTEGER,
            ypos    INTEGER,
            width   INTEGER,
            height  INTEGER,
            bgcolor TEXT,
            font    TEXT,
            fcolor  TEXT);''',

        'retrieve': 'SELECT * FROM notes;',

        'upsert': '''INSERT INTO notes(id, text, xpos, ypos, width, height, bgcolor, font, fcolor)
            VALUES(:id, :text, :xpos, :ypos, :width, :height, :bgcolor, :font, :fcolor)
            ON CONFLICT(id) DO UPDATE
            SET text = :text, xpos = :xpos, ypos = :ypos, width = :width, height = :height,
            bgcolor = :bgcolor, font = :font, fcolor = :fcolor WHERE id = :id;''',

        'update': '''UPDATE notes SET text = :text, xpos = :xpos, ypos = :ypos,
            width = :width, height = :height WHERE id = :id;''',

        'delete': 'DELETE FROM notes WHERE id = :id;',

        'pref_init': '''CREATE TABLE IF NOT EXISTS preferences (
            id      INTEGER     PRIMARY KEY,
            checked INTEGER        NOT NULL,
            bgcolor TEXT,
            font    TEXT,
            fcolor  TEXT);''',

        'pref_upsert': '''INSERT INTO preferences(id, checked, bgcolor, font, fcolor)
            VALUES (0, :checked, :bgcolor, :font, :fcolor)
            ON CONFLICT(id) DO UPDATE
            SET checked = :checked, bgcolor = :bgcolor, font = :font, fcolor = :fcolor WHERE id = 0;''',

        'pref_get': 'SELECT checked, bgcolor, font, fcolor FROM preferences WHERE id = 0;',
    }

    @HandleError(sqlite3.Error)
    def __init__(self, db:str) -> None:
        """ Initialize the database connection.

        Args:
            db (str): The path of the SQLite database file. """
        self.conn = sqlite3.connect(db)
        logger.info(f'SQLiteConnector::Connected to - {db}')
        self.execute_sql('init')
        self.execute_sql('pref_init')

    @HandleError(sqlite3.Error)
    def execute_sql(self, statement: str, values:dict|int={}) -> sqlite3.Cursor:
        if statement not in self.SQL:
            raise ValueError(f"Invalid SQL argument: {statement}")
        if isinstance(values, int):
            values = {'id': values} # convert to dict to pass as statement value

        with self.conn as connection:
            return connection.execute(self.SQL[statement], values)
