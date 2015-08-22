#-*- coding:utf-8 -*-

import log

from datetime import datetime

from tornado.escape import xhtml_escape

from helpers.base import DataProvider
from models.user import model as user_model

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User']


class User(DataProvider, user_model.User):
    pass


