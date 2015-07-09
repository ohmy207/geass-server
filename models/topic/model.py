#-*- coding:utf-8 -*-

from .base import *


class Topic(Model):

    name = 'topic'

    field = {
        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'authoruid':        (basestring, ''),

        'ispriv':           (bool, False)   ,
        'isanon':           (bool, False)   ,

        'pickeys':          (list, [])      ,

        'ctime':            (datetime, None),
    }


class Comment(Model):

    name = 'comment'

    field = {
        'tid':              (ObjectId, None),
        'content':          (basestring, ''),
        'authoruid':        (ObjectId, None),
        'up':               (list, [])      ,
        'size':             (int, 0)        ,
        'atime':            (datetime, None),
        'status':           (int, 0)        ,
    }
