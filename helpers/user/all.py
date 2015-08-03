#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.user import model as user

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User']


class User(user.User):

    @staticmethod
    def callback(record):
        result = {
            'uid': record['_id'],
            'nickname': record['nickname'] or record['open']['wx']['nickname'],
            'avatar': record['avatar'] or record['open']['wx']['headimgurl'],
            'sex': record['sex'] or record['open']['wx']['sex'],
        }

        return result

