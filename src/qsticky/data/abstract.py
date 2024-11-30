""" Defines helper classes for storing and retrieving NoteWidget state information. """
import logging
from abc import ABC, abstractmethod
from functools import wraps
from contextlib import closing

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__package__)

class StorageConnector(ABC):
    """ An abstract class for note-storing functionality. """
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """ Initialize storage container. """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> list[tuple]:
        """ Return a list of all stored notes. """
        raise NotImplementedError

    @abstractmethod
    def save(self, note: dict) -> bool:
        """ Save a note in the storage.

        Args:
            note (dict): Dictionary of note parameters.

        Returns:
            bool: True if note saved successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def update(self, note: dict) -> bool:
        """ Update note record in the storage.

        Args:
            note (dict): Dictionary of note parameters.

        Returns:
            bool: True if note updated successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def delete(self, rowid: int) -> bool:
        """ Delete note record from the storage.

        Args:
            rowid (int): The Id number of the note.

        Returns:
            bool: True if note deleted successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def get_preferences(self) -> tuple:
        """ Retrieve the application global preferences.

        Returns:
            tuple: A tuple of preferences (checked, bgcolor, font, fcolor). """
        raise NotImplementedError

    @abstractmethod
    def save_preferences(self, preferences:dict) -> bool:
        """ Save the global preferences.

        Args:
            preferences (dict): A dictionary representation of preference values.

        Returns:
            bool: True if preferences saved successfully, False otherwise. """
        raise NotImplementedError


class NoStorage(StorageConnector):
    """ Defines a dummy connector for no storage functionality. """
    def __init__(self) -> None:
        logger.warning(f'NoStorage::Running in memory')

    def retrieve(self) -> list[tuple]:
        return []

    def save(self, note: dict) -> bool:
        return True

    def update(self, note: dict) -> bool:
        return True

    def delete(self, rowid: int) -> bool:
        return True

    def get_preferences(self) -> tuple:
        return (0, '', '', '')

    def save_preferences(self, preferences: dict) -> bool:
        return True


class DataBaseConnector(StorageConnector):
    """ Defines aa abstract connector for SQL databases. """
    @abstractmethod
    def execute_sql(self, statement: str, values:dict|int={}) -> 'cursor':
        """ Execute SQL statement on the database.

        Args:
            statement (str): The key of SQL statement to execute from SQL statements dictionary.
            values (dict|tuple|int, optional): A dictionary representing the SQL statement values
                or note id. Defaults to None.

        Returns:
            cursor: A database cursor object with SQL query result (depends on used backend).

        Raises:
            ValueError: If the provided argument is invalid. """
        raise NotImplementedError

    def retrieve(self) -> list:
        with closing(self.execute_sql('retrieve')) as cursor:
            return cursor.fetchall()

    def save(self, note: dict) -> bool:
        with closing(self.execute_sql('upsert', note)) as cursor:
            return bool(cursor)

    def update(self, note: dict) -> bool:
        with closing(self.execute_sql('update', note)) as cursor:
            return bool(cursor)

    def delete(self, rowid: int) -> bool:
        with closing(self.execute_sql('delete', rowid)) as cursor:
            return bool(cursor)

    def get_preferences(self) -> tuple:
        with closing(self.execute_sql('pref_get')) as cursor:
            return cursor.fetchone()

    def save_preferences(self, preferences:dict) -> bool:
        with closing(self.execute_sql('pref_upsert', preferences)) as cursor:
            return bool(cursor)


class HandleError:
    """ Decorator class for catching and logging database errors. """
    def __init__(self, error):
        self.error = error

    def __call__(self, func):
        @wraps(func)
        def wrapper(obj: StorageConnector, *args, **kwargs):
            kwargs2 = dict(kwargs)
            if 'password' in kwargs2:
                kwargs2['password'] = '*****'  # Mask password for logging
            logger.debug(f'{type(obj).__name__}.{func.__name__}{args}{kwargs2}')
            try:
                return func(obj, *args, **kwargs)
            except self.error as e:
                logger.error(f'{type(obj).__name__}.{func.__name__} failed! Args: {args} Kwargs: {kwargs2}')
                QMessageBox.critical(
                    None,
                    'Error',
                    f'''An error occurred in {type(obj).__name__}.{func.__name__}
Args: {args} Kwargs: {kwargs2}

{e}'''
                )
                raise
        return wrapper
