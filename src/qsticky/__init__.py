""" Sticky desktop notes application. """
import sys
import os

__all__ = [
    'notes',
    'data',
    'preferences',
]
# Add QSticky's source code directory to the Python path.
sys.path.append(os.path.dirname(__file__))
# Load Qt-resource object code
import resources
