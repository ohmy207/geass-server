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

        'vote':             (list, [])      ,
        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class Comment(Model):

    name = 'comment'

    field = {
        'tid':              (ObjectId, None),
        'auid':             (ObjectId, None),
        'toauid':           (ObjectId, None),
        'topid':            (ObjectId, None),

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }
