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

