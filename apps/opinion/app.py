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


class OpinionsHandler(BaseHandler):

    _post_params = {
        'need': [
            ('content', basestring),
        ],
        'option': [
            ('pickeys', list, []),
        ]
    }

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
            # TODO
            ('type', basestring, 'all'),
        ]
    }

    #@authenticated
    def GET(self, tid):
        opinions = db_opinion['opinion'].get_all(
            {'tid': self.to_objectid(tid)},
            skip=self._skip,
            limit=self._limit
        )

        self._data = {
            'dataList': db_user['vote'].format_opinions(self.current_user, opinions),
            'nextStart': self._skip + self._limit
        }

    @authenticated
    def POST(self, tid):
        data = self._params

        tid = self.to_objectid(tid)
        topic = db_topic['topic'].find_one({'_id': tid})

        # TODO error code
        if not topic:
            raise ResponseError(404)

        data['tid'] = tid
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()
        data['istz'] = True if data['auid'] == topic['auid'] else False

        pid = db_opinion['opinion'].create(data)
        data['_id'] = pid

        self._data = db_opinion['opinion'].callback(db_opinion['opinion'].to_one_str(data))


class DetailOpinionHandler(BaseHandler):

    #@authenticated
    def GET(self, pid):
        uid = self.current_user

        data = db_opinion['opinion'].get_one(self.to_objectid(pid))
        data['is_voted'] = db_user['vote'].is_opinion_voted(uid, pid)
        data['title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']

        self._data = {
            'opinion': data,
            'has_user_voted': db_user['vote'].has_user_voted(uid, data['tid']),
        }

