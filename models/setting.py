# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
    user as _user,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
        'user': _user,
    },

    'db_file': {
    }
}
