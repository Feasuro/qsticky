#!/usr/bin/env python

import sqlite3

DBNAME = "resources/qsticky.db"
SQL = {
    'create': '''CREATE TABLE IF NOT EXISTS notes (
    id      INTEGER     PRIMARY KEY NOT NULL,
    title   TEXT        UNIQUE,
    text    TEXT        NOT NULL
    );''',
# NULL titles don't count for uniqueness!!!
    'insert': '''INSERT INTO notes(id, title, text)
    VALUES(:id, :title, :text)
    ;''',

    'update': 'UPDATE notes SET title=:title, text=:text WHERE id = :id',

    'upsert': '''INSERT INTO notes(id, title, text)
    VALUES(:id, :title, :text)
    ON CONFLICT(id) DO UPDATE
    SET title = :title,
        text = :text
    WHERE id = :id
    ;''',

    'fetch': 'SELECT id, title, text FROM notes;',

    'delete': 'DELETE FROM notes WHERE id = :id'
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
        """ Set instance atributes

        Keyword Arguments:
            text -- Note body. (default: {None})
            title -- Note title. (default: {None})
            id -- Database primary key. (default: {None})

        Raises:
            ValueError: If title is not unique.
            TypeError: If id is not integer.
        """
        # test for title uniqueness
        for note in self.data.values():
            if note is self:
                continue
            if title is not None and note.title == title:
                raise ValueError("title must be unique.")
        # if already in data only update text/title if provided
        if hasattr(self, 'id'):
            if title:
                self.title = title
            if text:
                self.text = text
        else:
            # pick smallest unused integer if id not provided
            if id is None:
                id = 0
                while id in self.data:
                    id += 1
            # setup all attributes
            if isinstance(id, int):
                self.id = id
            else:
                raise TypeError('Provide integer id value.')
            self.title = title
            self.text = text if text else ''
            # append to data
            self.data[self.id] = self

    def __repr__(self) -> str:
        """ Object representation as string """
        return f'<Note object {self.id}, title="{self.title}">'

    def __str__(self) -> str:
        """ How to print notes on the screen """
        return f'{self.title}\n{self.text}'

    def __eq__(self, other):
        """ Compare by title """
        return self.title == other.title
    
    def asdict(self) -> dict:
        """ Returns dictionary representation """
        return {'id': self.id,
                'title': self.title,
                'text': self.text}

    def save_del(self, command: str, dbpath: str=DBNAME) -> bool:
        """ Execute changes on database

        Arguments:
            command -- One of SQL statements

        Keyword Arguments:
            dbpath -- Database path (default: {DBNAME})

        Raises:
            KeyError: Wrong command

        Returns:
            Success or failure
        """
        try:
            conn = sqlite3.connect(dbpath, autocommit=False)
            conn.execute(SQL[command], self.asdict())
            conn.commit()
            conn.close()
        except KeyError as err:
            err.args += (f"'command' must be one of {list(SQL)}",)
            raise err
        except sqlite3.Error as err:
            print(err)
            return False
        else:
            return True

    @classmethod
    def fetch_db(cls, dbpath: str=DBNAME) -> bool:
        """ Fetch all notes from database and instantiate them

        Keyword Arguments:
            dbpath -- Database path (default: {DBNAME})

        Returns:
            Success or failure
        """
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
        else:
            return True if cls.data else False


if __name__ == '__main__':
    if Note.fetch_db():
        print("Succesfully connected with database and fetched notes:")
        print(Note.data)
    else:
        print("Something went wrong, or database is empty.")
