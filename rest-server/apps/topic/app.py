#-*- coding:utf-8 -*-

from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler
from apps.base import ResponseError

from helpers import topic as db_topic
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

        if len(data['title']) <= 0:
            raise ResponseError(51)

        data['uid'] = self.current_user
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
        spec = {'tid': tid}
        sort=[('vnum', -1), ('islz', -1), ('ctime', 1)]

        topic = db_topic['topic'].get_one({'_id': tid})
        if not topic:
            raise ResponseError(404)

        proposals = db_topic['proposal'].get_all(spec, skip=0, limit=5, sort=sort)

        sort=[('lnum', -1), ('islz', -1), ('ctime', 1)]
        opinions = db_topic['opinion'].get_all(spec, skip=0, limit=self._limit, sort=sort)

        self._data = {
            'topic': topic,
            'comments_count': db_user['comment'].find({'tid': tid, 'pid': None}).count(),
            'vote_total_num': db_user['vote'].find(spec).count(),
            'proposal_list': db_user['vote'].format_proposals(uid, proposals),
            'data_list': db_user['approve'].format_opinions(uid, opinions),
            'is_lz': topic['author_uid'] == unicode(uid),
            'has_user_voted': db_user['vote'].has_user_voted(uid, tid),
            'is_topic_followed': db_user['follow'].is_topic_followed(uid, tid),
            'next_start': self._skip + self._limit,
        }


class ProposalsHandler(BaseHandler):

    _post_params = {
        'need': [
            ('content', basestring),
        ],
        'option': [
            ('pickeys', list, []),
            #('isanon', bool, False),
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
        tid = self.to_objectid(tid)
        spec = {'tid': tid}
        sort=[('vnum', -1), ('islz', -1), ('ctime', 1)]

        proposals = db_topic['proposal'].get_all(
            spec=spec,
            skip=self._skip,
            limit=self._limit,
            sort=sort,
        )

        self._data = {
            'has_user_voted': db_user['vote'].has_user_voted(self.current_user, tid),
            'vote_total_num': db_user['vote'].find(spec).count(),
            'data_list': db_user['vote'].format_proposals(self.current_user, proposals),
            'next_start': self._skip + self._limit
        }

    @authenticated
    def POST(self, tid):
        data = self._params

        tid = self.to_objectid(tid)
        uid = self.current_user
        topic = db_topic['topic'].find_one({'_id': tid})
        is_lz = True if uid == topic['uid'] else False

        if not topic:
            raise ResponseError(50)

        if len(data['content']) <= 0:
            raise ResponseError(61)

        if len(data['pickeys']) > 8:
            raise ResponseError(62)

        data['tid'] = tid
        data['uid'] = uid
        data['ctime'] = datetime.now()
        data['islz'] = is_lz
        #if is_lz:
        #    data['isanon'] = topic['isanon']

        pid = db_topic['proposal'].create(data)
        data['_id'] = pid

        self._data = db_topic['proposal'].callback(db_topic['proposal'].to_one_str(data))


class DetailProposalHandler(BaseHandler):

    #@authenticated
    def GET(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)

        data = db_topic['proposal'].get_one({'_id': pid})
        if not data:
            raise ResponseError(404)

        tid = self.to_objectid(data['tid'])
        data['is_voted'] = db_user['vote'].is_proposal_voted(uid, pid)
        data['title'] = db_topic['topic'].find_one({'_id': tid}, {'title': 1})['title']

        self._data = {
            'proposal': data,
            #'comments_count': db_user['comment'].find({'pid': pid}).count(),
            'has_user_voted': db_user['vote'].has_user_voted(uid, data['tid']),
            'vote_total_num': db_user['vote'].find({'tid': tid}).count(),
        }


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
        spec = {'tid': self.to_objectid(tid)}
        sort=[('vnum', -1), ('islz', -1), ('ctime', 1)]

        opinions = db_topic['opinion'].get_all(
            spec=spec,
            skip=self._skip,
            limit=self._limit,
            sort=sort,
        )

        self._data = {
            'data_list': db_user['approve'].format_opinions(self.current_user, opinions),
            'next_start': self._skip + self._limit
        }

    @authenticated
    def POST(self, tid):
        data = self._params

        tid = self.to_objectid(tid)
        uid = self.current_user
        topic = db_topic['topic'].find_one({'_id': tid})
        opinion_count = db_topic['opinion'].find({'tid': tid, 'uid': uid}).count()
        is_lz = True if uid == topic['uid'] else False

        if not topic:
            raise ResponseError(50)

        #if opinion_count > 0:
        #    raise ResponseError(63)

        if len(data['content']) <= 0:
            raise ResponseError(61)

        if len(data['pickeys']) > 8:
            raise ResponseError(62)

        data['tid'] = tid
        data['uid'] = uid
        data['ctime'] = datetime.now()
        data['islz'] = is_lz
        if is_lz:
            data['isanon'] = topic['isanon']

        oid = db_topic['opinion'].create(data)
        data['_id'] = oid

        self._data = db_topic['opinion'].callback(db_topic['opinion'].to_one_str(data))


class DetailOpinionHandler(BaseHandler):

    #@authenticated
    def GET(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        data = db_topic['opinion'].get_one({'_id': oid})
        if not data:
            raise ResponseError(404)

        data['is_approved'] = db_user['approve'].is_opinion_approved(uid, oid)
        data['title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']

        self._data = {
            'opinion': data,
            #'comments_count': db_user['comment'].find({'tid': tid}).count(),
            'has_user_voted': db_user['vote'].has_user_voted(uid, data['tid']),
        }

