#-*- coding:utf-8 -*-

from .base import *


class Opinion(Model):

    name = 'opinion'

    field = {
        'tid':              (ObjectId, None),
        'auid':             (ObjectId, None),

        'isanon':           (bool, False)   ,

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }

