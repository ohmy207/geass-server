#-*- coding:utf-8 -*-

from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler
from apps.base import ResponseError

from helpers import topic as db_topic

logger = log.getLogger(__file__)


class NewTopicHandler(BaseHandler):

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
        data['auid'] = self.to_objectid(self.session['uid'])
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

    @authenticated
    def GET(self, tid):
        tid = db_topic['topic'].to_objectid(tid)

        topic = db_topic['topic'].get_one({'_id': tid})
        proposals = db_topic['proposal'].get_all({'tid': tid}, skip=self._skip, limit=self._limit)

        self._data = {
            'topic': topic,
            'dataList': proposals,
            'nextStart': self._skip + self._limit
        }


class NewProposalHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('content', basestring),
        ],
        'option': [
            ('pickeys', list, []),
        ]
    }

    @authenticated
    def POST(self):
        data = self._params

        tid = db_topic['proposal'].to_objectid(data['tid'])
        topic = db_topic['topic'].find_one({'_id': tid})

        # TODO error code
        if not topic:
            raise ResponseError(404)

        data['tid'] = tid
        data['auid'] = self.to_objectid(self.session['uid'])
        data['ctime'] = datetime.now()

        if data['auid'] == topic['auid']:
            data['istz'] = True

        pid = db_topic['proposal'].insert(data)
        data = db_topic['proposal'].get_one(pid)

        self._data = data


class ListProposalHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
            ('type', basestring, 'all'),
        ]
    }

    @authenticated
    def GET(self, tid):
        if self._params['type'] == 'default':
            spec = {'tid': db_topic['proposal'].to_objectid(tid)}
            data_list = db_topic['proposal'].get_all(spec, skip=0, limit=3)
            result = []
            for d in data_list:
                d['hotReply'] = True
                result.append(d)

            self._data = {
                'dataList': result,
                'nextStart': self._skip,
            }
            return

        spec = {'tid': db_topic['proposal'].to_objectid(tid)}
        data_list = db_topic['proposal'].get_all(spec, skip=self._skip, limit=self._limit)
        self._data = {
            'dataList': data_list,
            'nextStart': self._skip + self._limit
        }


class DetailProposalHandler(BaseHandler):

    @authenticated
    def GET(self, pid):
        data = db_topic['proposal'].get_one(db_topic['proposal'].to_objectid(pid))
        data['title'] = db_topic['topic'].find_one({'_id': db_topic['proposal'].to_objectid(data['tId'])}, {'title': 1})['title']

        self._data = {
            'proposal': data,
        }


class VoteProposalHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('pid', basestring),
        ],
        'option': [
        ]
    }

    @authenticated
    def POST(self):
        data = self._params
        uid = self.to_objectid(self.session['uid'])

        pid = db_topic['proposal'].to_objectid(data['pid'])
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(404)

        if uid in proposal['vote']:
            raise ResponseError(404)

        db_topic['proposal'].update({'_id': pid}, {'$inc': {'vnum': 1}, '$push': {'vote': uid}}, w=1)

        self._data = {
            'voteNum': 1,
        }


class NewCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('content', basestring),
        ],
        'option': [
            ('topid', basestring, None),
        ]
    }

    @authenticated
    def POST(self):
        data = self._params

        tid = db_topic['comment'].to_objectid(data['tid'])
        topic = db_topic['topic'].find_one({'_id': tid})

        # TODO error code
        if not topic:
            raise ResponseError(404)

        data['tid'] = db_topic['comment'].to_objectid(data['tid'])
        data['topid'] = db_topic['comment'].to_objectid(data['topid'])
        data['toauid'] = db_topic['comment'].find_one({'_id': data['topid']}).get('auid', None) if data['topid'] else None
        data['auid'] = self.to_objectid(self.session['uid'])
        data['ctime'] = datetime.now()

        if data['auid'] == topic['auid']:
            data['istz'] = True

        coid = db_topic['comment'].insert(data)
        data = db_topic['comment'].get_one(coid)

        self._data = data


class ListCommentHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    @authenticated
    def GET(self, tid):
        spec = {'tid': db_topic['comment'].to_objectid(tid)}
        data_list = db_topic['comment'].get_all(spec, skip=self._skip, limit=self._limit)

        self._data = {
            'dataList': data_list,
            'nextStart': self._skip + self._limit
        }


class LikeCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('coid', basestring),
        ],
        'option': [
        ]
    }

    @authenticated
    def POST(self):
        data = self._params
        uid = self.to_objectid(self.session['uid'])

        coid = db_topic['comment'].to_objectid(data['coid'])
        comment = db_topic['comment'].find_one({'_id': coid})

        if not comment:
            raise ResponseError(404)

        if uid in comment['like']:
            raise ResponseError(404)

        db_topic['comment'].update({'_id': coid}, {'$inc': {'lnum': 1}, '$push': {'like': uid}}, w=1)

        self._data = {
            'likeNum': 1,
        }
