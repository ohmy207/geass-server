#-*- coding:utf-8 -*-

from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler
from apps.base import ResponseError

from helpers import topic as db_topic
from helpers import opinion as db_opinion
from helpers import user as db_user

logger = log.getLogger(__file__)


class TopicsHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
            ('content', basestring),
        ],
        'option': [
            ('ispriv', bool, False),
            ('isanon', bool, False),
            ('pickeys', list, []),
        ]
    }

    @authenticated
    def POST(self):
        data = self._params
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()

        tid = db_topic['topic'].create(data)

        self._jump = '/topic?tid='+unicode(tid)


class DetailTopicHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    #@authenticated
    def GET(self, tid):
        tid = self.to_objectid(tid)
        uid = self.current_user
        spec = {'tid': tid, 'istz': True}
        sort=[('vnum', -1), ('ctime', 1)]

        topic = db_topic['topic'].get_one({'_id': tid})
        opinions = db_opinion['opinion'].get_all(spec, skip=0, limit=5, sort=sort)
        spec['istz'] = False
        opinions.extend(db_opinion['opinion'].get_all(
            spec,
            skip=self._skip,
            limit=self._limit,
            sort=sort
        ))

        self._data = {
            'topic': topic,
            'dataList': db_user['vote'].format_opinions(uid, opinions),
            'has_user_voted': db_user['vote'].has_user_voted(uid, tid),
            'is_topic_followed': db_user['follow'].is_topic_followed(uid, tid),
            'nextStart': self._skip + self._limit,
        }

