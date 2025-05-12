"""
Logging utilities for SteamLauncherGUI.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from steamlaunchergui.config.constants import LOG_FILE

def setup_logging(level=logging.INFO, log_file=LOG_FILE, max_bytes=5*1024*1024, backup_count=3):
    """
    Set up logging with rotation capabilities.
    
    Args:
        level: The logging level (default: INFO)
        log_file: Path to the log file (default: from constants)
        max_bytes: Maximum size of each log file before rotation (default: 5MB)
        backup_count: Number of backup files to keep (default: 3)
    """
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a rotating file handler if log_file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        logging.info(f"Log file: {os.path.abspath(log_file)}")
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Log startup information
    logging.info("SteamLauncherGUI logging initialized")
    logging.info(f"Log level: {logging.getLevelName(level)}")
    
    return root_logger

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        A logger instance
    """
    return logging.getLogger(name) 