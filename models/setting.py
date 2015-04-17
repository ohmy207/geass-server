# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
    },

    'db_file': {
    }
}
