# -*- coding:utf-8 -*-

import os

from pymongo import MongoClient

from . import setting


if os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test__')):
    mc = MongoClient(host='localhost:27017')
    print '-- IN DEBUG --'
else:
    mc = MongoClient(host='localhost:27017')


# topic
topic = mc['excalibur_topic']
user = mc['excalibur_user']
proposal = mc['excalibur_proposal']
