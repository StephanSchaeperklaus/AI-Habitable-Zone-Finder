#!/usr/bin/env python3
"""
Main entry point for the AIHabitablezone application.
Handles initialization and launches the GUI.
"""
import sys
import os
from pathlib import Path
import argparse
import logging
import importlib
from typing import Optional, List, Tuple

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from src.gui import launch_gui
from src.config import CONFIG, ConfigurationManager
from src.logger import LOGGER
from src.error import AIHabitablezoneError
from src.data import data_manager

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AIHabitablezone - Explore habitable zones and exoplanets"
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable data caching'
    )
    parser.add_argument(
        '--skip-deps-check',
        action='store_true',
        help='Skip dependency checking'
    )
    return parser.parse_args()

def setup_environment(args: argparse.Namespace) -> None:
    """
    Set up the application environment.
    
    Args:
        args: Parsed command line arguments
    """
    try:
        # Set up logging level
        if args.debug:
            LOGGER.setLevel(logging.DEBUG)
            LOGGER.debug("Debug logging enabled")
        
        # Create necessary directories
        app_dirs = ['data', 'logs', 'cache', 'plots', 'plots3d', 'temp']
        for directory in app_dirs:
            path = Path(CONFIG.data_dir) / directory
            path.mkdir(parents=True, exist_ok=True)
            LOGGER.debug(f"Created directory: {path}")
        
        # Load configuration if specified
        if args.config:
            config_path = Path(args.config)
            if config_path.exists():
                config_manager = ConfigurationManager(str(config_path))
                config_manager.load_config()
                LOGGER.info(f"Loaded configuration from {args.config}")
            else:
                LOGGER.warning(f"Configuration file not found: {args.config}")
        
        # Set cache behavior
        if args.no_cache:
            LOGGER.info("Data caching disabled")
            # You might want to add a no_cache flag to your data manager
            
    except Exception as e:
        LOGGER.error(f"Failed to set up environment: {str(e)}")
        raise AIHabitablezoneError("Environment setup failed", cause=e)

def check_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if all required dependencies are available.
    
    Returns:
        Tuple of (success: bool, missing_deps: List[str])
    """
    required_deps = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'astropy': 'astropy',
        'plotly': 'plotly',
        'tkinter': 'tkinter'
    }
    
    missing_deps = []
    
    for module_name, package_name in required_deps.items():
        try:
            importlib.import_module(module_name)
            LOGGER.debug(f"Found dependency: {module_name}")
        except ImportError:
            missing_deps.append(package_name)
            LOGGER.warning(f"Missing dependency: {package_name}")
    
    return len(missing_deps) == 0, missing_deps

def main() -> None:
    """Main application entry point."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Set up environment
        setup_environment(args)
        
        # Check dependencies unless skipped
        if not args.skip_deps_check:
            deps_ok, missing_deps = check_dependencies()
            if not deps_ok:
                deps_list = ", ".join(missing_deps)
                raise AIHabitablezoneError(
                    f"Missing dependencies: {deps_list}\n"
                    "Please install required dependencies using:\n"
                    "pip install -r requirements.txt"
                )
        
        # Initialize data manager
        LOGGER.info("Initializing data manager...")
        if not args.no_cache:
            # Attempt to load cached data
            try:
                data_manager.load_simulation_data()
                LOGGER.info("Loaded cached simulation data")
            except Exception as e:
                LOGGER.warning(f"Could not load cached data: {str(e)}")
        
        # Launch GUI
        LOGGER.info("Launching GUI...")
        launch_gui()
        
    except AIHabitablezoneError as e:
        LOGGER.error(f"Application error: {str(e)}")
        if e.cause:
            LOGGER.error(f"Caused by: {str(e.cause)}")
        sys.exit(1)
        
    except Exception as e:
        LOGGER.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
        
    finally:
        LOGGER.info("Application terminated")

if __name__ == "__main__":
    main()