# -*- coding:utf-8 -*-

import os

from pymongo import MongoClient

from config.global_setting import TEST_MODE


if TEST_MODE:
    mc = MongoClient(host='localhost:27017')
else:
    mc = MongoClient(host='localhost:27017')


# geass database
topic = mc['geass_topic']
opinion = mc['geass_opinion']
user = mc['geass_user']
