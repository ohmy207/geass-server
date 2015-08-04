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

    @staticmethod
    def callback(record):
        result = {
            'uid': record['_id'],
            'nickname': record['nickname'] or record['open']['wx']['nickname'],
            'avatar': record['avatar'] or record['open']['wx']['headimgurl'],
            'sex': record['sex'] or record['open']['wx']['sex'],
        }

        return result

