#-*- coding:utf-8 -*-

import log

from models.topic import model as topic

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic']


class Topic(topic.Topic):
    pass
