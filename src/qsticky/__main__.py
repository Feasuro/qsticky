""" Application entry point module, parses commandline input. """
import sys
import os
import logging

from PyQt6.QtCore import QCommandLineParser, QCommandLineOption

import qsticky.data as data
from qsticky.notes import NoteApplication, NoteWidget

logger = logging.getLogger(__name__)
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
        ['V', 'verbose'],
        tr('Print additional info.')
    ))
    parser.addOption(QCommandLineOption(
        ['D', 'debug'],
        tr('Even more verbose output.'),
    ))
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

    # Set up logging levels based on command-line options
    if parser.isSet('debug'):
        logging.basicConfig(level=logging.DEBUG)
    elif parser.isSet('verbose'):
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig()
    logger.debug(f'''{type(parser).__name__}::Specified: {parser.optionNames()}
###    type = {parser.value("type")}'''
    )
    # Choose database object to return
    match parser.value('type'):
        case 'sqlite':
            for opt in ['host', 'port', 'dbname', 'user', 'password']:
                if parser.isSet(opt):
                    logger.warning(f'{type(parser).__name__}::Ignoring option --{opt} {parser.value(opt)}')
            logger.debug(f'''{type(parser).__name__}::
###    sqlite-db = {parser.value("sqlite-db")}'''
            )
            return data.SQLiteConnector(parser.value('sqlite-db'))
        case 'postgre':
            if parser.isSet('f'):
                logger.warning(f'{type(parser).__name__}::Ignoring option --sqlite-db {parser.value('f')}')
            logger.debug(f'''{type(parser).__name__}::
###    host = {parser.value("host")}
###    port = {parser.value("port")}
###    dbname = {parser.value("dbname")}
###    user = {parser.value("user")}
###    password = {parser.value("password")}'''
            )
            if not data.has_postgre:
                logger.error('PostgreSQL database driver is not installed.')
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
            logger.error(f'Not recognized storage type: {parser.value('type')}')
            return data.NoStorage()


def main() -> int:
    """ Main function used to run the program. """
    app = NoteApplication(sys.argv)
    NoteWidget.db = parse_args(app)
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
