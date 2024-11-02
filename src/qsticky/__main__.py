#!/usr/bin/env python
import sys
import os

from notes import NoteApplication, NoteWidget
from data import SQLiteConnector

dir_path = __file__
for i in range(3):
    dir_path = os.path.dirname(dir_path)
    
# Save data in project root directory or in user's home directory or current directory
if os.path.basename(dir_path) != 'qsticky':
    dir_path = os.getenv('XDG_DATA_HOME', os.getcwd())

# Allow user to specify the database path via environment variable DBPATH
DBPATH = os.getenv('DBPATH', default=os.path.join(dir_path, 'qsticky.db'))

def main() -> int:
    app = NoteApplication(sys.argv)
    NoteWidget.db = SQLiteConnector(DBPATH)
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
