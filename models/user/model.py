
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


class Notice(Model):

    """
    action
        0: 预留
        1: 添加选项
        2: 添加看法
        3: 评论话题
        4: 评论看法
        5: 回复评论
        6: 投票
        7: 赞同看法

    paid: parent id
    """

    name = 'notice'

    field = {
        'uid':             (ObjectId, None),
        'paid':            (ObjectId, None),

        'parent':          (basestring, ''),

        'action':          (int, 0)        ,
        'count':           (int, 0)        ,

        'senders':         (list, [])      ,

        'ctime':           (datetime, None),
    }

