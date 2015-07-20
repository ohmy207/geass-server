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


class Proposal(Model):

    name = 'proposal'

    field = {
        'tid':              (ObjectId, None),
        'authoruid':        (ObjectId, None),

        'content':          (basestring, ''),

        'vote':             (list, [])      ,
        'pickeys':          (list, [])      ,

        'ctime':            (datetime, None),
    }
