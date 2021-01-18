from nonebot.default_config import *
from .mongoDB import mongo_client_kwargs, database

HOST = '127.0.0.1'
PORT = 8080

SUPERUSERS = {1234567890}
COMMAND_START = {''}
COMMAND_SEP = {'.', '-'}

APSCHEDULER_CONFIG.update({
    'apscheduler.jobstores.mongo': {
        'type': 'mongodb',
        'database': database, 'collection': 'collection_for_APScheduler'
    }.update(mongo_client_kwargs)
})
