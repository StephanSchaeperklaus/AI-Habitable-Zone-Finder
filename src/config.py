#!/usr/bin/env python3
"""
Configuration module for the AIHabitablezone application.
Provides a default configuration and supports loading configuration files.
"""

import json
import logging
from pathlib import Path

# Global configuration object.
class Config:
    # Default configuration values
    data_dir = str(Path(__file__).parent.parent.resolve())  # Root directory of the project

# Use a simple instance as the global config
CONFIG = Config()

class ConfigurationManager:
    """
    Manages loading and updating configuration values from a JSON file.
    """
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.logger = logging.getLogger("AIHabitablezone")

    def load_config(self) -> None:
        """
        Load configuration from the specified JSON file and update the global CONFIG.
        """
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            # Update the global CONFIG attributes if they exist in the loaded data.
            for key, value in config_data.items():
                if hasattr(CONFIG, key):
                    setattr(CONFIG, key, value)
                    self.logger.debug(f"Config parameter updated: {key} = {value}")
                else:
                    # Optionally, add new attributes
                    setattr(CONFIG, key, value)
                    self.logger.debug(f"New config parameter added: {key} = {value}")
            self.logger.info("Configuration successfully loaded.")
        except Exception as e:
            self.logger.error(f"Failed to load config file: {self.config_file} - {e}")
            raise