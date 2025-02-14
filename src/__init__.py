"""
AIHabitablezone package initialization.
"""

__version__ = '0.1.0'

from .error import (
    AIHabitablezoneError,
    ConfigurationError,
    DataError,
    DataLoadError,
    DataValidationError,
    PhysicsError,
    VisualizationError,
    GUIError
)

from .config import CONFIG, ConfigurationManager
from .logger import LOGGER
from .data import data_manager
from .gui import launch_gui

__all__ = [
    'AIHabitablezoneError',
    'ConfigurationError',
    'DataError',
    'DataLoadError',
    'DataValidationError',
    'PhysicsError',
    'VisualizationError',
    'GUIError',
    'CONFIG',
    'ConfigurationManager',
    'LOGGER',
    'data_manager',
    'launch_gui'
]