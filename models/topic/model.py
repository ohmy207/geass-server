#-*- coding:utf-8 -*-

from .base import *


class Topic(Model):

    name = 'topic'

    field = {
        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'uid':              (basestring, ''),

        'ispriv':           (bool, False)   ,
        'isanon':           (bool, False)   ,

        'pickeys':          (list, [])      ,

        'ctime':            (datetime, None),
    }


class Proposal(Model):

    name = 'proposal'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        #'isanon':           (bool, False)   ,

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class Opinion(Model):

    name = 'opinion'

    field = {
        'tid':              (ObjectId, None),
        'pid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'isanon':           (bool, False)   ,

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'anum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }

