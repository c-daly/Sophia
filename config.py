"""
Backward compatibility layer for the old config.py interface.

This module provides a same interface as the old config.py but uses
the new centralized configuration system under the hood.
"""

import logging

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

# Placeholder for milvus and mongo - will be initialized lazily
milvus = None
mongo = None

def get_mongo():
    """Get the MongoDB wrapper instance."""
    global mongo
    if mongo is None:
        from data.mongo_wrapper import MongoWrapper
        mongo = MongoWrapper()
    return mongo

# Initialize mongo for immediate backward compatibility
try:
    mongo = get_mongo()
except Exception:
    # If mongo fails to initialize, leave it as None
    pass
debug = False
