import logging
from data.mongo_wrapper import MongoWrapper

mongo = MongoWrapper()
logger = logging.getLogger('sophia')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
