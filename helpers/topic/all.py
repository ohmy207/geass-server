#-*- coding:utf-8 -*-

import loggers

from models.topic import model as topic

logger = loggers.getLogger(__file__)

MODEL_SLOTS = ['Topic']


class Topic(topic.Topic):
    pass
