# -*- coding:utf-8 -*-

import os

from pymongo import MongoClient

from config.global_setting import TEST_MODE


if TEST_MODE:
    mc = MongoClient(host='localhost:27017')
else:
    mc = MongoClient(host='localhost:27017')


# topic
topic = mc['excalibur_topic']
user = mc['excalibur_user']
opinion = mc['excalibur_opinion']
comment = mc['excalibur_comment']
