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

__all__ = [
    "abstract",
    "sqlite",
    "psql",
]
