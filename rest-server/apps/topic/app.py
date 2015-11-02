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
        ],
        'option': [
            ('content', basestring, ''),
            ('isanon', bool, False),
            ('pickeys', list, []),
        ]
    }

    @authenticated
    def POST(self):
        data = self._params
        uid = self.current_user

        if len(data['title']) <= 0:
            raise ResponseError(30)

        data['uid'] = uid
        data['ctime'] = datetime.now()

        tid = db_topic['topic'].create(data)
        db_topic['public_edit'].add_log(
            'topics', tid, uid, {'title': data['title'], 'content': data['content'], 'pickeys': data['pickeys']})

        self._jump = '/topic?tid='+unicode(tid)


class OneTopicHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
        ],
        'option': [
            ('content', basestring, ''),
            ('isanon', bool, False),
            ('pickeys', list, []),
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
        uid = self.current_user
        spec = {'tid': tid}
        sort=[('vnum', -1), ('ctime', 1)]
        topic = db_topic['topic'].get_one({'_id': tid})

        if not topic:
            raise ResponseError(404)

        proposals = db_topic['proposal'].get_all(spec, skip=0, limit=5, sort=sort)

        sort=[('lnum', -1), ('ctime', 1)]
        opinions = db_topic['opinion'].get_all(spec, skip=0, limit=self._limit, sort=sort)

        self._data = {
            'topic': topic,
            'proposals': db_user['vote'].format_proposals(uid, proposals),
            'data_list': db_user['approve'].format_opinions(uid, opinions),

            'comments_count': db_topic['comment'].get_comments_count('topics', tid),
            'vote_total_num': db_user['vote'].find(spec).count(),

            'is_author': topic['author_uid'] == unicode(uid),
            'has_user_voted': db_user['vote'].has_user_voted(uid, tid),
            'is_topic_followed': db_user['follow'].is_topic_followed(uid, tid),
            'has_more_proposals': True if db_topic['proposal'].get_all(spec, skip=5, limit=1, sort=sort) else False,

            'next_start': self._skip + self._limit,
        }

    @authenticated
    def POST(self, tid):
        data = self._params
        tid = self.to_objectid(tid)
        uid = self.current_user

        topic = db_topic['topic'].find_one({'_id': tid})

        if not topic:
            raise ResponseError(404)

        if len(data['title']) <= 0:
            raise ResponseError(30)

        if len(data['pickeys']) > 8:
            raise ResponseError(31)

        if uid != topic['uid']:
            data.pop('isanon')

        db_topic['topic'].update({'_id': tid}, {'$set': data})
        db_user['notice'].update_notice(tid, 9)
        db_topic['public_edit'].add_log(
            'topics', tid, uid, {'title': data['title'], 'content': data['content'], 'pickeys': data['pickeys']})

        topic.update(data)
        self._data = db_topic['topic'].callback(db_topic['topic'].to_one_str(topic))


class ProposalsHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
        ],
        'option': [
            ('content', basestring, ''),
            ('pickeys', list, []),
        ]
    }

    _get_params = {
        'need': [
        ],
        'option': [
            ('type', basestring, None),
        ]
    }

    #@authenticated
    def GET(self, tid):
        tid = self.to_objectid(tid)
        spec = {'tid': tid}
        sort=[('vnum', -1), ('ctime', 1)]

        proposals = []
        has_more_proposals = False
        if self._params['type'] == 'more':
            proposals = db_topic['proposal'].get_all(spec, skip=5, limit=10, sort=sort)
            has_more_proposals = True if db_topic['proposal'].get_all(spec, skip=15, limit=1, sort=sort) else False
        if self._params['type'] == 'all':
            proposals = db_topic['proposal'].get_all(spec, skip=15, limit=100, sort=sort)

        self._data = {
            'data_list': db_user['vote'].format_proposals(self.current_user, proposals),
            'has_more_proposals': has_more_proposals,
            'has_user_voted': db_user['vote'].has_user_voted(self.current_user, tid),
            'vote_total_num': db_user['vote'].find(spec).count(),
            #'next_start': self._skip + self._limit
        }

    @authenticated
    def POST(self, tid):
        data = self._params
        tid = self.to_objectid(tid)
        uid = self.current_user

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if len(data['title']) <= 0:
            raise ResponseError(30)

        if len(data['pickeys']) > 8:
            raise ResponseError(31)

        data['tid'] = tid
        data['uid'] = uid
        data['ctime'] = datetime.now()

        pid = db_topic['proposal'].create(data)
        db_user['notice'].update_notice(tid, 1)
        db_topic['public_edit'].add_log(
            'proposals', pid, uid, {'title': data['title'], 'content': data['content'], 'pickeys': data['pickeys']})

        data['_id'] = pid
        self._data = db_topic['proposal'].callback(db_topic['proposal'].to_one_str(data))


class OneProposalHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
        ],
        'option': [
            ('content', basestring, ''),
            ('pickeys', list, []),
        ]
    }

    #@authenticated
    def GET(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)

        record = db_topic['proposal'].find_one({'_id': pid})
        if not record:
            raise ResponseError(404)

        tid = record['tid']
        proposal = db_topic['proposal'].callback(db_topic['proposal'].to_one_str(record))
        proposal['is_voted'] = db_user['vote'].is_proposal_voted(uid, pid)
        proposal['topic_title'] = db_topic['topic'].find_one({'_id': tid}, {'title': 1})['title']

        self._data = {
            'proposal': proposal,
            'has_user_voted': db_user['vote'].has_user_voted(uid, tid),
            'vote_total_num': db_user['vote'].find({'tid': tid}).count(),
        }

    @authenticated
    def POST(self, pid):
        data = self._params
        pid = self.to_objectid(pid)
        uid = self.current_user

        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(404)

        if len(data['title']) <= 0:
            raise ResponseError(30)

        if len(data['pickeys']) > 8:
            raise ResponseError(31)

        db_topic['proposal'].update({'_id': pid}, {'$set': data})
        db_topic['public_edit'].add_log(
            'proposals', pid, uid, {'title': data['title'], 'content': data['content'], 'pickeys': data['pickeys']})

        proposal.update(data)
        self._data = db_topic['proposal'].callback(db_topic['proposal'].to_one_str(proposal))


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
        sort=[('vnum', -1), ('ctime', 1)]

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

        if not topic:
            raise ResponseError(404)

        #if opinion_count > 0:
        #    raise ResponseError(71)

        if len(data['content']) <= 0:
            raise ResponseError(30)

        if len(data['pickeys']) > 8:
            raise ResponseError(31)

        data['tid'] = tid
        data['uid'] = uid
        data['ctime'] = datetime.now()

        oid = db_topic['opinion'].create(data)
        db_user['notice'].update_notice(tid, 2)
        data['_id'] = oid

        self._data = db_topic['opinion'].callback(db_topic['opinion'].to_one_str(data))


class OneOpinionHandler(BaseHandler):

    _post_params = {
        'need': [
            ('content', basestring),
        ],
        'option': [
            ('pickeys', list, []),
            ('isanon', bool, False),
        ]
    }

    #@authenticated
    def GET(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        data = db_topic['opinion'].get_one({'_id': oid})
        if not data:
            raise ResponseError(404)

        data['is_approved'] = db_user['approve'].is_opinion_approved(uid, oid)
        data['topic_title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']

        self._data = {
            'opinion': data,
            'is_author': data['author_uid'] == unicode(uid),
            'comments_count': db_topic['comment'].get_comments_count('opinions', oid),
            'has_user_voted': db_user['vote'].has_user_voted(uid, data['tid']),
        }

    @authenticated
    def POST(self, oid):
        data = self._params
        oid = self.to_objectid(oid)
        uid = self.current_user

        opinion = db_topic['opinion'].find_one({'_id': oid})

        if not opinion:
            raise ResponseError(404)

        if len(data['content']) <= 0:
            raise ResponseError(30)

        if len(data['pickeys']) > 8:
            raise ResponseError(31)

        if uid != opinion['uid']:
            raise ResponseError(403)

        db_topic['opinion'].update({'_id': oid}, {'$set': data})
        opinion.update(data)

        self._data = db_topic['opinion'].callback(db_topic['opinion'].to_one_str(opinion))


class CommentsHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    _post_params = {
        'need': [
            ('content', basestring),
        ],
        'option': [
            ('tocoid', basestring, None),
        ]
    }

    def GET(self, parent, parent_id):
        data_list = db_topic['comment'].get_comments(
            parent=parent,
            parent_id=parent_id,
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit,
        )

        self._data = {
            'data_list': data_list,
            'next_start': self._skip + self._limit
        }

    @authenticated
    def POST(self, parent, parent_id):
        uid = self.current_user
        parent_id = self.to_objectid(parent_id)

        if len(self._params['content']) <= 0:
            raise ResponseError(30)

        spec = {'_id': parent_id}
        parent_rd = db_topic['topic'].find_one(spec) if parent == 'topics' else db_topic['opinion'].find_one(spec)

        if not parent_rd:
            raise ResponseError(404)

        data = db_topic['comment'].add_comment(
            parent=parent, parent_id=parent_id, uid=uid, content=self._params['content'],
            tocoid=self._params['tocoid'], is_lz=parent_rd['uid']==uid)

        action = 3 if parent == 'topics' else 5
        if data['target']:
            action = 4 if parent == 'topics' else 6

        db_user['notice'].update_notice(parent_id, action, data['target'].get('uid', None))

        self._data = data

