#-*- coding:utf-8 -*-

import log

from models.topic import model as topic_model
from helpers.base import BaseHelper, UserHelper
from config.global_setting import PIC_URL, ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic']


class Topic(BaseHelper, topic_model.Topic):

    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid':  record['_id'],
            'title': record['title'],
            'author_uid': record['auid'],
            'is_private': record['ispriv'],
            #'is_anonymous': record['isanon'],
        }

        result['content'] = Topic.xhtml_escape(record['content'])
        result['f_created_time'] = Topic._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        if record['isanon']:
            result['author'] = ANONYMOUS_USER['nickname']
            result['avatar'] = ANONYMOUS_USER['avatar']
        else:
            simple_user = Topic._user.get_simple_user(record['auid'])
            result['author'] = simple_user['nickname']
            result['avatar'] = simple_user['avatar']

        return result

