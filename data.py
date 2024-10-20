import os
from abc import ABC, abstractmethod

DEBUG = os.getenv('DEBUG')

class DataBaseConnector(ABC):
    """ An abstract class for note-storing functionality. """
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """ Open a database connection. """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> list:
        """ Return a list of all notes in the database. """
        raise NotImplementedError

    @abstractmethod
    def save(self, note: dict) -> bool:
        """ Save a note in the database.

        Args:
            note (dict): Database record of note as a dictionary.

        Returns:
            bool: True if note saved successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def update(self, note: dict) -> bool:
        """ Update a note in the database.

        Args:
            note (dict): Database record of note as a dictionary.

        Returns:
            bool: True if note saved successfully, False otherwise. """
        raise NotImplementedError

    @abstractmethod
    def delete(self, rowid: int) -> bool:
        """ Delete a note from the database.

        Args:
            rowid (int): The ID of the note.

        Returns:
            bool: True if note deleted successfully, False otherwise. """
        raise NotImplementedError
