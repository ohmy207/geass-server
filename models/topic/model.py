#-*- coding:utf-8 -*-

from .base import *


class Topic(Model):

    name = 'topic'

    field = {
        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'auid':             (basestring, ''),

        'ispriv':           (bool, False)   ,
        'isanon':           (bool, False)   ,

        'pickeys':          (list, [])      ,

        'ctime':            (datetime, None),
    }

