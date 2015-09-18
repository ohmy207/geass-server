#-*- coding:utf-8 -*-

import log

from models.opinion import model as opinion_model
from helpers.base import BaseHelper, UserHelper
from config.global_setting import PIC_URL, ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Opinion']


class Opinion(BaseHelper, opinion_model.Opinion):

    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['uid'],
            'vote_num': record['vnum'],
            'is_tz': record['istz'],
            'is_voted': False,
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

