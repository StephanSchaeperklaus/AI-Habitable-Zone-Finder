#!/usr/bin/env python3
"""
Custom error definitions for the AIHabitablezone application.
"""

class AIHabitablezoneError(Exception):
    """
    Base exception class for AIHabitablezone-specific errors.
    Optionally stores an underlying cause exception.
    """
    def __init__(self, message: str, cause: Exception = None) -> None:
        super().__init__(message)
        self.cause = cause

class ConfigurationError(AIHabitablezoneError):
    """Raised when configuration loading or validation fails."""
    pass

class DataError(AIHabitablezoneError):
    """Base class for data-related errors."""
    pass

class DataLoadError(DataError):
    """Raised when loading data from files or APIs fails."""
    pass

class DataValidationError(DataError):
    """Raised when data validation fails."""
    pass

class PhysicsError(AIHabitablezoneError):
    """Raised when physics calculations fail."""
    pass

class VisualizationError(AIHabitablezoneError):
    """Raised when visualization operations fail."""
    pass

class GUIError(AIHabitablezoneError):
    """Raised when GUI operations fail."""
    pass