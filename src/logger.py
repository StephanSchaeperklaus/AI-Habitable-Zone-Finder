#!/usr/bin/env python3
"""
Logger module for the AIHabitablezone application.
Initializes a logger with stream and file handlers.
"""

import logging
from pathlib import Path
from src.config import CONFIG

# Configure basic logger settings
LOGGER = logging.getLogger("AIHabitablezone")
LOGGER.setLevel(logging.INFO)  # Default level; can be overridden (e.g., to DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
console_handler.setFormatter(console_formatter)
LOGGER.addHandler(console_handler)

# Optionally add a file handler if logs directory exists in CONFIG.data_dir/logs
logs_path = Path(CONFIG.data_dir) / "logs"
logs_path.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(logs_path / "application.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
LOGGER.addHandler(file_handler)