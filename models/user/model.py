
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
        4: 回复话题评论
        5: 评论看法
        6: 回复看法评论
        7: 赞同看法
        8: 投票

    paid: parent id
    """

    name = 'notice'

    field = {
        'uid':             (ObjectId, None),
        'paid':            (ObjectId, None),

        'action':          (int, 0)        ,

        'isread':          (bool, False)   ,

        'ctime':           (datetime, None),
    }

