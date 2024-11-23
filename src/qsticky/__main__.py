""" Application entry point module, parses commandline input. """
import sys
import os

from PyQt6.QtCore import QCommandLineParser, QCommandLineOption, qDebug, qWarning

import qsticky.data as data
from qsticky.notes import NoteApplication, NoteWidget

tr = lambda string: NoteApplication.translate('main', string)

def parse_args(app: NoteApplication) -> data.StorageConnector:
    """ Parse command-line arguments and connect to the specified database.

    Args:
        app (NoteApplication): The application object.

    Returns:
        data.StorageConnector: Connection helper object."""
    # Set up the parser, description and default options
    parser = QCommandLineParser()
    parser.setApplicationDescription("Show sticky notes on your desktop.")
    parser.addHelpOption()
    parser.addVersionOption()
    # Add custom command line options
    parser.addOption(QCommandLineOption(
        ['t', 'type'],
        tr('The database engine to connect with.\ndefault: sqlite'),
        'sqlite|none|postgre',
        'sqlite'
    ))
    default_dir = os.getenv('XDG_DATA_HOME', default=os.path.expanduser('~/.local/share'))
    parser.addOption(QCommandLineOption(
        ['f', 'sqlite-db'],
        tr('SQLite database file path.\ndefault: ~/.local/share/qsticky.db'),
        'file',
        os.path.join(default_dir, 'qsticky.db')
    ))
    parser.addOption(QCommandLineOption(
        ['o', 'host'],
        tr('The hostname or IP address of the database server.\ndefault: UNIX socket connection.'),
        'host'
    ))
    parser.addOption(QCommandLineOption(
        ['p', 'port'],
        tr('The port number to connect to.\ndefault: 5432'),
        'port',
        '5432'
    ))
    parser.addOption(QCommandLineOption(
        ['d', 'dbname'],
        tr('The name of the database.\ndefault: qsticky'),
        'database',
        'qsticky'
    ))
    parser.addOption(QCommandLineOption(
        ['u', 'user'],
        tr('The username to authenticate with.\ndefault: current system username'),
        'user',
        os.getenv('USER')
    ))
    parser.addOption(QCommandLineOption(
        ['s', 'password'],
        tr('The password to authenticate with.\ndefault: an empty string'),
        'password'
    ))

    # Process the command-line arguments
    parser.process(app)
    qDebug(f'''
DEBUG: {parser})
###    Specified: {parser.optionNames()}
###    type = {parser.value("type")} {type(parser.value("type"))}
###    sqlite-db = {parser.value("sqlite-db")} {type(parser.value("sqlite-db"))}
###    host = {parser.value("host")} {type(parser.value("host"))}
###    port = {parser.value("port")} {type(parser.value("port"))}
###    dbname = {parser.value("dbname")} {type(parser.value("dbname"))}
###    user = {parser.value("user")} {type(parser.value("user"))}
###    password = {parser.value("password")} {type(parser.value("password"))}'''
)
    # Choose database object to return
    match parser.value('type'):
        case 'sqlite':
            return data.SQLiteConnector(parser.value('sqlite-db'))
        case 'postgre':
            if not data.has_postgre:
                qWarning('WARNING: PostgreSQL database driver is not installed.')
                return data.NoStorage()
            return data.PostgreSQLConnector(
                host=parser.value('host'),
                port=parser.value('port'),
                dbname=parser.value('dbname'),
                user=parser.value('user'),
                password=parser.value('password')
            )
        case 'none':
            return data.NoStorage()
        case _:
            qWarning(f'WARNING: Not recognized storage type: {parser.value('type')}')
            return data.NoStorage()


def main() -> int:
    """ Main function used to run the program. """
    app = NoteApplication(sys.argv)
    NoteWidget.db = parse_args(app)
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
