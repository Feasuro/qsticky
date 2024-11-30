""" Defines class of MySQL connector.
For storing NoteWidget instances in MySQL database. """
import logging

import MySQLdb

from qsticky.data.abstract import DataBaseConnector, HandleError

logger = logging.getLogger(__package__)

class MySQLConnector(DataBaseConnector):
    """ MySQL database connector class. """
    SQL = {
        'init': '''CREATE TABLE IF NOT EXISTS notes (
            id      INTEGER     PRIMARY KEY,
            text    TEXT        NOT NULL,
            xpos    INTEGER     NOT NULL,
            ypos    INTEGER     NOT NULL,
            width   INTEGER     NOT NULL,
            height  INTEGER     NOT NULL,
            bgcolor TEXT        NOT NULL,
            font    TEXT        NOT NULL,
            fcolor  TEXT        NOT NULL);''',

        'retrieve': 'SELECT * FROM notes;',

        'upsert': '''INSERT INTO notes(id, text, xpos, ypos, width, height, bgcolor, font, fcolor)
            VALUES(%(id)s, %(text)s, %(xpos)s, %(ypos)s, %(width)s, %(height)s, %(bgcolor)s, %(font)s, %(fcolor)s)
            ON DUPLICATE KEY UPDATE
            text = %(text)s, xpos = %(xpos)s, ypos = %(ypos)s, width = %(width)s, height = %(height)s,
            bgcolor = %(bgcolor)s, font = %(font)s, fcolor = %(fcolor)s;''',

        'update': '''UPDATE notes SET text = %(text)s, xpos = %(xpos)s, ypos = %(ypos)s,
            width = %(width)s, height = %(height)s WHERE id = %(id)s;''',

        'delete': 'DELETE FROM notes WHERE id = %(id)s;',

        'pref_init': '''CREATE TABLE IF NOT EXISTS preferences (
            id      INTEGER     PRIMARY KEY,
            checked INTEGER     NOT NULL,
            bgcolor TEXT        NOT NULL,
            font    TEXT        NOT NULL,
            fcolor  TEXT        NOT NULL);''',

        'pref_upsert': '''INSERT INTO preferences(id, checked, bgcolor, font, fcolor)
            VALUES (0, %(checked)s, %(bgcolor)s, %(font)s, %(fcolor)s)
            ON DUPLICATE KEY UPDATE
            checked = %(checked)s, bgcolor = %(bgcolor)s, font = %(font)s, fcolor = %(fcolor)s;''',

        'pref_get': 'SELECT checked, bgcolor, font, fcolor FROM preferences WHERE id = 0;',
    }

    @HandleError(MySQLdb.Error)
    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        """ Initialize the database connection.

        Args:
            host (str): The host of the MySQL server.
            port (str): The port of the MySQL server.
            dbname (str): The name of the database.
            user (str): The username for database access.
            password (str): The password for database access. """
        self.conn = MySQLdb.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        logger.info(f"MySQLConnector::Connected to - {self.conn.get_server_info()} at {self.conn.get_host_info()}")
        self.execute_sql('init')
        self.execute_sql('pref_init')

    @HandleError(MySQLdb.Error)
    def execute_sql(self, statement: str, values:dict|int={}):# -> MySQLdb.cursors.Cursor:
        if statement not in self.SQL:
            raise ValueError(f"Invalid SQL key argument: {statement}")
        if isinstance(values, int):
            values = {'id': values} # convert to dict to pass as statement value

        cursor = self.conn.cursor()
        cursor.execute(self.SQL[statement], values)
        self.conn.commit()
        return cursor
