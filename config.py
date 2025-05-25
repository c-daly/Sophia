import logging
from data.mongo_wrapper import MongoWrapper

# milvus takes forever to load
milvus = None
#mongo = MongoWrapper()
logger = logging.getLogger('sophia')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
