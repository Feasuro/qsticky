""" Subpackage with classes that perform tasks related to storing notes. """
from .abstract import StorageConnector, NoStorage, DataBaseConnector
from .sqlite import SQLiteConnector

try:
    import psycopg2
except ImportError:
    has_postgre = False
else:
    has_postgre = True
    from .psql import PostgreSQLConnector

try:
    import MySQLdb
except ImportError:
    has_mysql = False
else:
    has_mysql = True
    from .mysql import MySQLConnector

__all__ = [
    "abstract",
    "sqlite",
    "psql",
    "mysql",
]
