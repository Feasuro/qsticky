#!/usr/bin/env python
import sys
import os

from notes import NoteApplication, NoteWidget
from data import SQLiteConnector

db_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../resources/qsticky.db'))
DBPATH = os.getenv('DBPATH', default=db_path)

def main() -> int:
    app = NoteApplication(sys.argv)
    NoteWidget.db = SQLiteConnector(DBPATH)
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
