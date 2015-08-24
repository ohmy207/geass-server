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


class Proposal(Model):

    name = 'proposal'

    field = {
        'tid':              (ObjectId, None),
        'auid':             (ObjectId, None),

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class Vote2Proposal(Model):

    name = 'vote2proposal'

    field = {
        'tid':             (ObjectId, None),
        'pid':             (ObjectId, None),
        'uid':             (ObjectId, None),
    }


class Comment(Model):

    name = 'comment'

    field = {
        'tid':              (ObjectId, None),
        'auid':             (ObjectId, None),
        'toauid':           (ObjectId, None),
        'tocoid':           (ObjectId, None),

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }

