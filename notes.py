#!/usr/bin/env python

import sqlite3

DBNAME = "resources/qsticky.db"
SQL = {
    'create': '''CREATE TABLE IF NOT EXISTS notes (
    id      INTEGER     PRIMARY KEY NOT NULL,
    title   TEXT        UNIQUE,
    text    TEXT        NOT NULL
    );''',

    'insert': '''INSERT INTO notes(id, title, text)
    VALUES(?, ?, ?)
    ;''',

    'update': 'UPDATE notes SET title=?, text=? WHERE id = ?',

    'upsert': '''INSERT INTO notes(id, title, text)
    VALUES(?, ?, ?)
    ON CONFLICT(id) DO UPDATE
    SET title = ?,
        text = ?
    WHERE id = ?
    ;''',

    'fetch': 'SELECT id, title, text FROM notes;',
}

class Note():
    """ Serializer/Deserializer class for storing notes """
    data = {}
    
    def __new__(cls, id:int=None, *args, **kwargs):
        """ First check if such id exists already """
        if id in cls.data:
            return cls.data[id]
        else:
            return object.__new__(cls)

    def __init__(self, text:str=None, title:str=None, id:int=None) -> None:
        """ Set instance atributes """
        if hasattr(self, 'id'):
            print('DEBUG1')
            if title:
                self.title = title
            if text:
                self.text = text
        else:
            print('DEBUG2')
            if id is None:
                id = 0
                while id in self.data:
                    id += 1

            if isinstance(id, int):
                self.id = id
            else:
                raise TypeError('Provide integer id value.')
            self.title = title
            self.text = text if text else ''

            self.data[self.id] = self
            '''try:
                if not self.conn:
                    self.conn = sqlite3.connect(DBNAME, autocommit=False)
                self.conn.execute(SQL['insert'], (self.id, self.title, self.text))
                self.conn.commit()
                self.conn.close()
                self.conn = None
            except sqlite3.Error as err:
                print(err)'''

    def __repr__(self) -> str:
        """ Object representation as string """
        return f'<Note object {self.id}, title="{self.title}">'

    def __str__(self) -> str:
        """ How to print notes on the screen """
        return f'{self.title}\n{self.text}'

    def __eq__(self, other):
        """ Compare by title """
        return self.title == other.title

    def save(self, dbpath: str) -> bool:
        """ Save note to database """
        try:
            conn = sqlite3.connect(dbpath, autocommit=False)
            conn.execute(SQL['update'], (self.title, self.text, self.id))
            conn.commit()
            conn.close()
        except sqlite3.Error as err:
            print(err)
            return False
        else:
            return True

    @classmethod
    def sync_db(cls, dbpath: str) -> bool:
        try:
            conn = sqlite3.connect(dbpath, autocommit=False)
            conn.execute(SQL['create'])
            query = conn.execute(SQL['fetch'])
            conn.commit()
            for id, title, text in query.fetchall():
                cls.data[id] = Note(text, title, id)
            conn.close()
        except sqlite3.Error as err:
            print(err)
            return False
        finally:
                return True if cls.data else False


if __name__ == '__main__':
    print(Note.sync_db(DBNAME))
    print(Note.data)
    #print(Note.data[1])
