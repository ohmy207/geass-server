# -*- coding:utf-8 -*-

# change name
from db.conn import (
    topic as _topic,
    proposal as _proposal,
)

MONGO_DB_MAPPING = {
    'db': {
        'topic': _topic,
        'proposal': _proposal,
    },

    'db_file': {
    }
}
