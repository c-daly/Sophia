"""
config.py
This module provides configuration management for the application.
"""
import logging
import json

milvus = None
mongo = None
logger = None
env = "dev"

log_init = False

class Configurator:
    """Configurator class to manage configurations."""

    def __init__(self, log_level=logging.DEBUG, env_name='dev'):
        self.env_name = env_name
        self.config = self.load_config(env_name)
        self.logger = self.init_logger(name='sophia', log_level=log_level)
        self.log_level = log_level

    def load_config(self, env_name):
        """Load the configuration from a file."""
        #try:
        #    with open(f'config/{env_name}.json', 'r') as f:
        #        return json.load(f)
        #except FileNotFoundError:
        #    raise FileNotFoundError(f"Configuration file for environment '{env_name}' not found.")
        pass

    def init_logger(self, name='sophia', log_level=logging.DEBUG) -> logging.Logger:
        """
        Initialize and return a logger instance.
        Args:
            name (str): Name of the logger.
            log_level (int): Logging level.
        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger

