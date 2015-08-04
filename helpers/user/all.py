#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.user import model as user

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User']


class User(user.User):
    pass

