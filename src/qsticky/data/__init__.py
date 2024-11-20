""" Subpackage with classes that perform tasks related to storing notes. """
from .data import * # deprecated module
from .abstract import *
from .sqlite import *
try:
    import psycopg2
except ImportError:
    has_postgre = False
else:
    has_postgre = True
    from.psql import *

__all__ = [
    "abstract",
    "sqlite",
    "psql",
]
