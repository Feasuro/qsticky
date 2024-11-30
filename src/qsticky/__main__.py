""" Application entry point module, parses commandline input. """
import sys
import os
import logging

from PyQt6.QtCore import QCommandLineParser, QCommandLineOption

import qsticky.data as data
from qsticky.notes import NoteApplication, NoteWidget

logger = logging.getLogger(__name__)

class ArgumentParser(QCommandLineParser):
    """ Command-line argument parser for QSticky. """
    tr = lambda obj, string: NoteApplication.translate(type(obj).__name__, string)
    default_dir = os.getenv('XDG_DATA_HOME', default=os.path.expanduser('~/.local/share'))
    def __init__(self) -> None:
        super().__init__()
        self.connector = data.NoStorage
        self.params = {}
        self.setApplicationDescription(self.tr('Show sticky notes on your desktop.'))
        self.addHelpOption()
        self.addVersionOption()
        # Add custom command line options
        self.addOption(QCommandLineOption(
            ['V', 'verbose'],
            self.tr('Print additional info.')
        ))
        self.addOption(QCommandLineOption(
            ['D', 'debug'],
            self.tr('Even more verbose output.'),
        ))
        self.addOption(QCommandLineOption(
            ['t', 'type'],
            self.tr('The database engine to connect with.\ndefault: sqlite'),
            'sqlite|none|postgre|mysql',
            'sqlite'
        ))
        self.addOption(QCommandLineOption(
            ['f', 'sqlite-db'],
            self.tr('SQLite database file path.\ndefault: ~/.local/share/qsticky.db'),
            'file',
            os.path.join(self.default_dir, 'qsticky.db')
        ))
        self.addOption(QCommandLineOption(
            ['o', 'host'],
            self.tr('The hostname or IP address of the database server.\ndefault: UNIX socket connection.'),
            'host'
        ))
        self.addOption(QCommandLineOption(
            ['p', 'port'],
            self.tr('The port number to connect to.\ndefault: 5432'),
            'port',
            '5432'
        ))
        self.addOption(QCommandLineOption(
            ['d', 'dbname'],
            self.tr('The name of the database.\ndefault: qsticky'),
            'database',
            'qsticky'
        ))
        self.addOption(QCommandLineOption(
            ['u', 'user'],
            self.tr('The username to authenticate with.\ndefault: current system username'),
            'user',
            os.getenv('USER')
        ))
        self.addOption(QCommandLineOption(
            ['s', 'password'],
            self.tr('The password to authenticate with.\ndefault: an empty string'),
            'password'
        ))

    def process(self, app: NoteApplication) -> None:
        """ Process command-line arguments. """
        super().process(app)
        self.setup_logging()
        self.setup_connection()

    def setup_logging(self) -> None:
        """ Set up logging levels based on command-line arguments. """
        if self.isSet('debug'):
            logging.basicConfig(level=logging.DEBUG)
        elif self.isSet('verbose'):
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig()

    def setup_connection(self) -> None:
        """ Choose apropriate StorageConnector and connect to the specified database. """
        logger.debug(f'{type(self).__name__}::Specified: {self.optionNames()}')
        match self.value('type'):

            case 'sqlite':
                for opt in ['host', 'port', 'dbname', 'user', 'password']:
                    if self.isSet(opt):
                        logger.warning(f'{type(self).__name__}::Ignoring option --{opt} {self.value(opt)}')
                self.params['db'] = self.value('sqlite-db')
                self.connector = data.SQLiteConnector

            case 'postgre':
                if self.isSet('sqlite-db'):
                    logger.warning(f'{type(self).__name__}::Ignoring option --sqlite-db {self.value('f')}')
                self.params = {
                    'host': self.value('host'),
                    'port': self.value('port'),
                    'dbname': self.value('dbname'),
                    'user': self.value('user'),
                    'password': self.value('password')
                }
                if not data.has_postgre:
                    logger.error('PostgreSQL database driver is not installed.')
                else:
                    self.connector = data.PostgreSQLConnector

            case 'mysql':
                if self.isSet('sqlite-db'):
                    logger.warning(f'{type(self).__name__}::Ignoring option --sqlite-db {self.value('f')}')
                self.params = {
                    'host': self.value('host'),
                    'port': int(self.value('port')) if self.isSet('port') else 3306,
                    'database': self.value('dbname'),
                    'user': self.value('user'),
                    'password': self.value('password')
                }
                if not data.has_mysql:
                    logger.error('MySQL database driver is not installed.')
                else:
                    self.connector = data.MySQLConnector

            case 'none':
                for opt in ['sqlite-db', 'host', 'port', 'dbname', 'user', 'password']:
                    if self.isSet(opt):
                        logger.warning(f'{type(self).__name__}::Ignoring option --{opt} {self.value(opt)}')

            case _:
                logger.error(f'Not recognized storage type: {self.value('type')}')

    def connect(self) -> data.StorageConnector:
        """ Connect to the specified database and return the StorageConnector. """
        try:
            return self.connector(**self.params)
        except Exception as error:
            logger.error(f'{type(self).__name__}::Error connecting to database: {error}')
            return data.NoStorage()

def main() -> int:
    """ Main function used to run the program. """
    app = NoteApplication(sys.argv)
    parser = ArgumentParser()
    parser.process(app)
    NoteWidget.db = parser.connect()
    app.start()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
