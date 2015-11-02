#-*- coding:utf-8 -*-

from .base import *


class Topic(Model):

    name = 'topic'

    field = {
        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'uid':              (ObjectId, None),

        #'ispriv':           (bool, False)   ,
        'isanon':           (bool, False)   ,

        'pickeys':          (list, [])      ,

        'ctime':            (datetime, None),
    }


class Proposal(Model):

    name = 'proposal'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'vnum':             (int, 0)        ,

        'ctime':            (datetime, None),
    }


class Opinion(Model):

    name = 'opinion'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'isanon':           (bool, False)   ,

        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'anum':             (int, 0)        ,

        'ctime':            (datetime, None),
    }


class TopicComment(Model):

    name = 'topic_comment'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),
        'target':           (dict, {})      ,

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class OpinionComment(Model):

    name = 'opinion_comment'

    field = {
        'oid':              (ObjectId, None),
        'uid':              (ObjectId, None),
        'target':           (dict, {})      ,

        'content':          (basestring, ''),

        'like':             (list, [])      ,

        'lnum':             (int, 0)        ,

        'islz':             (bool, False)   ,

        'ctime':            (datetime, None),
    }


class TopicEditLog(Model):

    name = 'topic_edit_log'

    field = {
        'tid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'status':           (int, 0)        ,

        'ctime':            (datetime, None),
    }


class ProposalEditLog(Model):

    name = 'proposal_edit_log'

    field = {
        'pid':              (ObjectId, None),
        'uid':              (ObjectId, None),

        'title':            (basestring, ''),
        'content':          (basestring, ''),

        'pickeys':          (list, [])      ,

        'status':           (int, 0)        ,

        'ctime':            (datetime, None),
    }

