#-*- coding:utf-8 -*-

import log

from models.topic import model as topic_model
from helpers.base import BaseHelper, UserHelper
from config.global_setting import PIC_URL, ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Opinion']


class Topic(BaseHelper, topic_model.Topic):

    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid':  record['_id'],
            'title': record['title'],
            'author_uid': record['uid'],
            'is_private': record['ispriv'],
            #'is_anonymous': record['isanon'],
        }

        result['content'] = Topic.xhtml_escape(record['content'])
        result['f_created_time'] = Topic._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        #if record['isanon']:
        #    result['author'] = ANONYMOUS_USER['nickname']
        #    result['avatar'] = ANONYMOUS_USER['avatar']
        #else:
        #    simple_user = Topic._user.get_simple_user(record['uid'])
        #    result['author'] = simple_user['nickname']
        #    result['avatar'] = simple_user['avatar']

        return result


class Proposal(BaseHelper, topic_model.Proposal):

    _topic = Topic()
    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['uid'],
            'vote_num': record['vnum'],
            'is_lz': record['islz'],
            'is_voted': False,
        }

        result['content'] = Opinion.xhtml_escape(record['content'])
        result['f_created_time'] = Opinion._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        return result


class Opinion(BaseHelper, topic_model.Opinion):

    _proposal = Proposal()
    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['pid'],
            'oid': record['_id'],
            'author_uid': record['uid'],
            'approve_num': record['anum'],
            'is_lz': record['islz'],
            'is_approved': False,
        }

        result['content'] = Opinion.xhtml_escape(record['content'])
        result['f_created_time'] = Opinion._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        if record['isanon']:
            result['author'] = ANONYMOUS_USER['nickname']
            result['avatar'] = ANONYMOUS_USER['avatar']
        else:
            simple_user = Opinion._user.get_simple_user(record['uid'])
            result['author'] = simple_user['nickname']
            result['avatar'] = simple_user['avatar']

        return result

