#-*- coding:utf-8 -*-

from .base import *


class Opinion(Model):

    name = 'opinion'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'isanon':           (bool, False)   ,

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }

