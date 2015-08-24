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

    @authenticated
    def GET(self, tid):
        tid = self.to_objectid(tid)
        uid = self.current_user

        topic = db_topic['topic'].get_one({'_id': tid})
        proposals = db_topic['proposal'].get_proposals(tid, uid=uid, skip=self._skip, limit=self._limit, first=1)
        has_voted = db_topic['proposal'].is_voted({'tid': tid, 'uid': uid})

        self._data = {
            'topic': topic,
            'dataList': proposals,
            'nextStart': self._skip + self._limit,
            'has_voted': has_voted,
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

        tid = self.to_objectid(data['tid'])
        topic = db_topic['topic'].find_one({'_id': tid})

        # TODO error code
        if not topic:
            raise ResponseError(404)

        data['tid'] = tid
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()
        data['istz'] = True if data['auid'] == topic['auid'] else False

        pid = db_topic['proposal'].create(data)
        data['_id'] = pid

        self._data = db_topic['proposal'].format(db_topic['proposal'].to_one_str(data), data['auid'])


class ListProposalHandler(BaseHandler):

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

    @authenticated
    def GET(self, tid):
        # TODO tz default
        proposals = db_topic['proposal'].get_proposals(tid, uid=self.current_user, skip=self._skip, limit=self._limit)

        self._data = {
            'dataList': proposals,
            'nextStart': self._skip + self._limit
        }


class DetailProposalHandler(BaseHandler):

    @authenticated
    def GET(self, pid):
        data = db_topic['proposal'].get_one(self.to_objectid(pid))
        data = db_topic['proposal'].format(data, self.current_user)
        data['title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']

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
    def POST(self, route):
        uid = self.current_user
        pid = self.to_objectid(self._params['pid'])
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['proposal'].find_one({'_id': pid, 'tid': tid}):
            raise ResponseError(404)

        self.route(route, tid, pid, uid)

    def do_vote(self, tid, pid, uid):
        if db_topic['proposal'].is_voted({'uid': uid, 'tid': tid}):
            raise ResponseError(404)

        db_topic['proposal']._vote2proposal.create({'tid': tid, 'pid': pid, 'uid': uid})
        db_topic['proposal'].update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)

    def do_unvote(self, tid, pid, uid):
        if not db_topic['proposal'].is_voted({'uid': uid, 'tid': tid}):
            raise ResponseError(404)

        db_topic['proposal']._vote2proposal.remove({'tid': tid, 'pid': pid, 'uid': uid})
        db_topic['proposal'].update({'_id': pid}, {'$inc': {'vnum': -1}}, w=1)

    def do_revote(self, tid, pid, uid):
        if db_topic['proposal'].is_voted({'uid': uid, 'tid': tid, 'pid': pid}):
            raise ResponseError(404)

        old_proposal = db_topic['proposal']._vote2proposal.find_one({'tid': tid, 'uid': uid})
        if not old_proposal:
            raise ResponseError(404)
        old_pid = old_proposal['pid']

        db_topic['proposal']._vote2proposal.remove({'tid': tid, 'uid': uid})
        db_topic['proposal'].update({'_id': old_pid}, {'$inc': {'vnum': -1}}, w=1)

        db_topic['proposal']._vote2proposal.create({'tid': tid, 'pid': pid, 'uid': uid})
        db_topic['proposal'].update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)


class NewCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('content', basestring),
        ],
        'option': [
            ('tocoid', basestring, None),
        ]
    }

    @authenticated
    def POST(self):
        data = self._params

        tid = self.to_objectid(data['tid'])
        topic = db_topic['topic'].find_one({'_id': tid})

        # TODO error code
        if not topic:
            raise ResponseError(404)

        data['tid'] = tid
        data['tocoid'] = self.to_objectid(data['tocoid'])
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()
        data['istz'] = True if data['auid'] == topic['auid'] else False

        to_comment = db_topic['comment'].find_one({'_id': data['tocoid']}, {'auid': 1}) if data['tocoid'] else None
        data['toauid'] = to_comment['auid'] if to_comment else None

        coid = db_topic['comment'].create(data)
        data['_id'] = coid

        self._data = db_topic['comment'].format(db_topic['comment'].to_one_str(data), data['auid'])


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
        data_list = db_topic['comment'].get_comments(self.to_objectid(tid), uid=self.current_user, skip=self._skip, limit=self._limit)

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
        uid = self.current_user

        coid = self.to_objectid(data['coid'])
        comment = db_topic['comment'].find_one({'_id': coid})

        if not comment:
            raise ResponseError(404)

        if uid in comment['like']:
            raise ResponseError(404)

        db_topic['comment'].update({'_id': coid}, {'$inc': {'lnum': 1}, '$push': {'like': uid}}, w=1)

