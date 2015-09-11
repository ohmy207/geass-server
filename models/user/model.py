#-*- coding:utf-8 -*-

from .base import *
from config.global_setting import PIC_URL


class User(Model):

    name = 'user'

    field = {
        'nickname':         (basestring, ''),
        'open':             (dict, {})      ,
        'sex':              (basestring, ''),
        'avatar':           (basestring, ''),
    }

    @staticmethod
    def callback(record):
        result = {
            'uid': record['_id'],
            'nickname': record['nickname'] or record['open']['wx']['nickname'],
            'avatar': PIC_URL['avatar'](record['avatar']) if record['avatar'] else record['open']['wx']['headimgurl'],
            'sex': record['sex'] or record['open']['wx']['sex'],
        }

        return result


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

