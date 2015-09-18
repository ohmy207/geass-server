#-*- coding:utf-8 -*-

import log

from models.topic import model as topic_model
from models.opinion import model as opinion_model
from helpers.base import BaseHelper, UserHelper
from config.global_setting import PIC_URL, ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Opinion']


class Opinion(BaseHelper, opinion_model.Opinion):

    _user = UserHelper()
    _topic = topic_model.Topic()

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

        is_anonymous = record['isanon']
        if record['islz']:
            topic = Opinion._topic.find_one(
                {'_id': Opinion.to_objectid(record['tid'])},
                {'isanon': 1}
            )
            is_anonymous = topic['isanon']

        if is_anonymous:
            result['author'] = ANONYMOUS_USER['nickname']
            result['avatar'] = ANONYMOUS_USER['avatar']
        else:
            simple_user = Opinion._user.get_simple_user(record['uid'])
            result['author'] = simple_user['nickname']
            result['avatar'] = simple_user['avatar']

        return result

