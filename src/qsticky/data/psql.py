import psycopg2

from PyQt6.QtCore import qInfo, qDebug

from qsticky.data import DataBaseConnector, CatchError


class PostgreSQLConnector(DataBaseConnector):
    """ PostgreSQL database connector class. """
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
            VALUES(%(id)s, %(text)s, %(xpos)s, %(ypos)s, %(width)s, %(height)s, %(bgcolor)s, %(font)s, %(fcolor)s)
            ON CONFLICT(id) DO UPDATE
            SET text = %(text)s, xpos = %(xpos)s, ypos = %(ypos)s, width = %(width)s, height = %(height)s,
            bgcolor = %(bgcolor)s, font = %(font)s, fcolor = %(fcolor)s RETURNING id;''',

        'update': '''UPDATE notes SET text = %(text)s, xpos = %(xpos)s, ypos = %(ypos)s,
            width = %(width)s, height = %(height)s WHERE id = %(id)s;''',

        'delete': 'DELETE FROM notes WHERE id = %(id)s;',

        'pref_init': '''CREATE TABLE IF NOT EXISTS preferences (
            id      INTEGER     PRIMARY KEY,
            checked INTEGER        NOT NULL,
            bgcolor TEXT,
            font    TEXT,
            fcolor  TEXT);''',

        'pref_upsert': '''INSERT INTO preferences(id, checked, bgcolor, font, fcolor)
            VALUES (0, %(checked)s, %(bgcolor)s, %(font)s, %(fcolor)s)
            ON CONFLICT(id) DO UPDATE
            SET checked = %(checked)s, bgcolor = %(bgcolor)s, font = %(font)s, fcolor = %(fcolor)s''',

        'pref_get': 'SELECT checked, bgcolor, font, fcolor FROM preferences WHERE id = 0;',
    }

    @CatchError(psycopg2.Error)
    def __init__(self, host: str, port: str, dbname: str, user: str, password: str) -> None:
        """ Initialize the database connection.

        Args:
            host (str): The host of the PostgreSQL server.
            port (str): The port of the PostgreSQL server.
            dbname (str): The name of the database.
            user (str): The username for database access.
            password (str): The password for database access. """
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )

        cursor = self.conn.cursor()
        cursor.execute("SELECT version();")
        query = cursor.fetchone()
        qInfo(f"INFO : Connected to - {query[0]}")
        qDebug("DEBUG: PostgreSQL server information:")
        qDebug(str(self.conn.get_dsn_parameters()))
        cursor.close()

    @CatchError(psycopg2.Error)
    def execute_sql(self, statement: str, values:dict|int={}) -> psycopg2.extensions.cursor:
        if statement not in self.SQL:
            raise ValueError(f"Invalid SQL argument: {statement}")
        if isinstance(values, int):
            values = {'id': values} # convert to dict to pass as statement value
        qInfo(f"INFO : Executing SQL: '{statement}' with values: {values}")

        cursor = self.conn.cursor()
        cursor.execute(self.SQL[statement], values)
        self.conn.commit()
        return cursor

    def save(self, note: dict) -> int:
        """ Override save method because PSQL doesn't support OID's and lastrowid is always 0 """
        return self.execute_sql('upsert', note).fetchone()[0]
