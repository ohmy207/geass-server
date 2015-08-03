# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
    proposal as _proposal,
    comment as _comment,
    user as _user,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
        'proposal': _proposal,
        'comment': _comment,
        'user': _user,
    },

    'db_file': {
    }
}
