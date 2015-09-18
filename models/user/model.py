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
        'uid':              (ObjectId, None),
        'touid':            (ObjectId, None),
        'tocoid':           (ObjectId, None),

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'istz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class Follow2Topic(Model):

    name = 'follow2topic'

    field = {
        'uid':             (ObjectId, None),
        'tid':             (ObjectId, None),
        'ctime':           (datetime, None),
    }


class Vote2Opinion(Model):

    name = 'vote2opinion'

    field = {
        'tid':             (ObjectId, None),
        'pid':             (ObjectId, None),
        'uid':             (ObjectId, None),
        'ctime':           (datetime, None),
    }

