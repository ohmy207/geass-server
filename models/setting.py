# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
    opinion as _opinion,
    comment as _comment,
    user as _user,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
        'opinion': _opinion,
        'comment': _comment,
        'user': _user,
    },

    'db_file': {
    }
}
