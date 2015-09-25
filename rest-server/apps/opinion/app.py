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
            ('isanon', bool, False),
        ]
    }

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
        spec = {'tid': self.to_objectid(tid), 'islz': False}
        sort=[('vnum', -1), ('ctime', 1)]

        opinions = db_opinion['opinion'].get_all(
            spec=spec,
            skip=self._skip,
            limit=self._limit,
            sort=sort,
        )

        self._data = {
            'data_list': db_user['vote'].format_opinions(self.current_user, opinions),
            'next_start': self._skip + self._limit
        }

    @authenticated
    def POST(self, tid):
        data = self._params

        tid = self.to_objectid(tid)
        uid = self.current_user
        topic = db_topic['topic'].find_one({'_id': tid})
        opinion_count = db_opinion['opinion'].find({'tid': tid, 'uid': uid}).count()
        is_lz = True if uid == topic['uid'] else False

        if not topic:
            raise ResponseError(50)

        if not is_lz and opinion_count > 0:
            raise ResponseError(63)

        if is_lz and opinion_count > 2:
            raise ResponseError(64)

        if len(data['content']) <= 0:
            raise ResponseError(61)

        if len(data['pickeys']) > 8:
            raise ResponseError(62)

        data['tid'] = tid
        data['uid'] = uid
        data['ctime'] = datetime.now()
        data['islz'] = is_lz

        pid = db_opinion['opinion'].create(data)
        data['_id'] = pid

        self._data = db_opinion['opinion'].callback(db_opinion['opinion'].to_one_str(data))


class DetailOpinionHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    #@authenticated
    def GET(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)

        data = db_opinion['opinion'].get_one({'_id': pid})
        if not data:
            raise ResponseError(404)

        data['is_voted'] = db_user['vote'].is_opinion_voted(uid, pid)
        data['title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']

        data_list = db_user['comment'].get_comments(
            tid=data['tid'],
            pid=pid,
            uid=uid,
            skip=self._skip,
            limit=self._limit,
            sort = [('lnum', -1), ('ctime', 1)],
        )

        self._data = {
            'opinion': data,
            'data_list': data_list,
            'comments_count': db_user['comment'].find({'pid': pid}).count(),
            'has_user_voted': db_user['vote'].has_user_voted(uid, data['tid']),
        }

