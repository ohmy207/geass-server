# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
    opinion as _opinion,
    user as _user,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
        'opinion': _opinion,
        'user': _user,
    },

    'db_file': {
    }
}
