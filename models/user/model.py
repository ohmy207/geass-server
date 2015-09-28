#-*- coding:utf-8 -*-

from .base import *


class User(Model):

    name = 'user'

    field = {
        'nickname':         (basestring, ''),
        'open':             (dict, {})      ,
        'sex':              (basestring, ''),
        'avatar':           (basestring, ''),
    }


class Comment(Model):

    name = 'comment'

    field = {
        'tid':              (ObjectId, None),
        'pid':              (ObjectId, None),
        'oid':              (ObjectId, None),
        'uid':              (ObjectId, None),
        'target':           (dict, {})      ,

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class Follow2Topic(Model):

    name = 'follow2topic'

    field = {
        'uid':             (ObjectId, None),
        'tid':             (ObjectId, None),
        'ctime':           (datetime, None),
    }


class Vote2Proposal(Model):

    name = 'vote2proposal'

    field = {
        'tid':             (ObjectId, None),
        'pid':             (ObjectId, None),
        'uid':             (ObjectId, None),
        'ctime':           (datetime, None),
    }


class Approve2Opinion(Model):

    name = 'approve2opinion'

    field = {
        'oid':             (ObjectId, None),
        'uid':             (ObjectId, None),
        'ctime':           (datetime, None),
    }

