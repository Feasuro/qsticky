""" Application entry point module. """
import sys
import os

from qsticky.notes import NoteApplication, NoteWidget
from qsticky.data import SQLiteConnector

dir_path = os.getenv('XDG_DATA_HOME', default=os.path.expanduser('~/.local/share'))

# Allow user to specify the database path via environment variable DBPATH
DBPATH = os.getenv('DBPATH', default=os.path.join(dir_path, 'qsticky.db'))

def main() -> int:
    """ Main function used to run the program. """
    print(f"### DBPATH = {DBPATH}", file=sys.stderr)
    app = NoteApplication(sys.argv)
    NoteWidget.db = SQLiteConnector(DBPATH)
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
