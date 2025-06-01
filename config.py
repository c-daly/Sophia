"""
Centralized configuration module for the Sophia project.
"""

import logging
import json

# For backward compatibility, provide the essential components
# Note: Due to import path conflicts, some modules should migrate to direct config imports

# Create a basic logger for backward compatibility
# milvus takes forever to load
milvus = None
mongo = None # MongoWrapper()
logger = logging.getLogger('sophia')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
env = "dev"

# Placeholder for milvus and mongo - will be initialized lazily
milvus = None
mongo = None

def get_config(args):
    """Get the configuration dictionary."""
    return {
        "debug": args.debug,
        "logger": logger,
            }

def load_config(env_name):
    """ Load the config from env specific configuration file. """
    # load config/dev.json
    try:
        with open(f'config/{env}.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file for environment '{env_name}' not found.")

def get_logger():
    """Get the logger instance."""
    return logger

def get_mongo():
    """Get the MongoDB wrapper instance."""
    global mongo
    if mongo is None:
        from data.mongo_wrapper import MongoWrapper
        mongo = MongoWrapper()
    return mongo

def get_environment():
    """"Get the environment configuration."""
    return env

