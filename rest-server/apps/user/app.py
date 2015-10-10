#-*- coding:utf-8 -*-

from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler
from apps.base import ResponseError

from helpers import topic as db_topic
from helpers import user as db_user

logger = log.getLogger(__file__)


class PersonalHandler(BaseHandler):

    @authenticated
    def GET(self):
        uid = self.current_user

        self._data = {
            'user': db_user['user'].get_one({'_id': uid}),
            'follow_topics': {},
            'publish_topics': {},
            'publish_opinions': {},
        }
        self._data['follow_topics']['count'] = db_user['follow'].get_follows_count(uid)
        self._data['publish_topics']['count'] = db_topic['topic'].find({'uid': uid}).count()
        self._data['publish_opinions']['count'] = db_topic['opinion'].find({'uid': uid}).count()

        self._data['follow_topics']['data_list'] = db_user['follow'].get_follow_topics(uid=uid, skip=0, limit=3)
        self._data['publish_topics']['data_list'] = db_user['user'].get_user_topics(uid=uid, skip=0, limit=3)
        self._data['publish_opinions']['data_list'] = db_user['user'].get_user_opinions(uid=uid, skip=0, limit=3)


class PublishingHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 10),
        ]
    }

    @authenticated
    def GET(self, route):
        uid = self.current_user
        self._data = {
            'next_start': self._skip + self._limit,
        }

        self.route(route, uid)

    def do_topics(self, uid):
        self._data['data_list'] = db_user['user'].get_user_topics(
            uid=uid,
            skip=self._skip,
            limit=self._limit,
        )

    def do_opinions(self, uid):
        self._data['data_list'] = db_user['user'].get_user_opinions(
            uid=uid,
            skip=self._skip,
            limit=self._limit,
        )


class FollowingHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
        ],
        'option': [
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

    _delete_params = _post_params

    @authenticated
    def GET(self):

        self._data = {
            'next_start': self._skip + self._limit,
        }

        self._data['data_list'] = db_user['follow'].get_follow_topics(
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit
        )

    @authenticated
    def POST(self):
        uid = self.current_user
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(50)

        if db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(80)

        db_user['follow'].follow_topic(uid, tid)

    @authenticated
    def DELETE(self):
        uid = self.current_user
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(50)

        if not db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(80)

        db_user['follow'].unfollow_topic(uid, tid)


class NewsHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    @authenticated
    def GET(self, route):
        self._data = {
            'next_start': self._skip + self._limit,
        }

        self.route(route)

    def do_topics(self):
        uid = self.current_user
        topics = db_topic['topic'].get_all({'uid': uid}, skip=self._skip, limit=self._limit, sort=[('rtime', -1)])

        data_list = []
        for t in topics:
            tid = self.to_objectid(t['tid'])
            opinions = db_topic['opinion'].get_all({'tid': tid}, skip=0, limit=2, sort=[('ctime', -1)])
            if not opinions:
                continue
            t['op_count'] = db_topic['opinion'].find({'tid': tid}).count()
            t['op_authors'] = [op['author'] for op in opinions]
            data_list.append(t)

        self._data['data_list'] = data_list

    def do_votes(self):
        opinions = db_topic['opinion'].get_all(
            {'uid': self.current_user, 'vnum': {'$gt': 0}},
            skip=self._skip,
            limit=self._limit,
            sort=[('vtime', -1)]
        )

        data_list = []
        for op in opinions:
            pid = self.to_objectid(op['pid'])
            votes = db_user['vote'].find({'pid': pid}, skip=0, limit=2, sort=[('ctime', -1)])
            op['vote_users'] = [db_user['user'].get_simple_user(v['uid'])['nickname'] for v in votes]
            op['title'] = db_topic['topic'].get_one({'_id': self.to_objectid(op['tid'])})['title']
            data_list.append(op)

        self._data['data_list'] = data_list

    def do_comments(self):
        comments = db_topic['comment'].get_all(
            {'target.uid': self.current_user},
            skip=self._skip,
            limit=self._limit,
            sort=[('ctime', -1)]
        )

        self._data['data_list'] = comments


# TODO code repeat
class VoteProposalHandler(BaseHandler):

    @authenticated
    def POST(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(60)

        tid = proposal['tid']
        if db_user['vote'].has_user_voted(uid, tid):
            raise ResponseError(90)

        db_user['vote'].vote_proposal(tid, pid, uid)

    @authenticated
    def DELETE(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(60)

        if not db_user['vote'].is_proposal_voted(uid, pid):
            raise ResponseError(91)

        db_user['vote'].unvote_proposal(proposal['tid'], pid, uid)

    def PATCH(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(60)

        tid = proposal['tid']
        if not db_user['vote'].has_user_voted(uid, tid) or db_user['vote'].is_proposal_voted(uid, pid):
            raise ResponseError(92)

        voted_proposal = db_user['vote'].find_one({'tid': tid, 'uid': uid})
        if not voted_proposal:
            raise ResponseError(93)

        db_user['vote'].unvote_proposal(tid, voted_proposal['pid'], uid)
        db_user['vote'].vote_proposal(tid, pid, uid)


class ApproveOpinionHandler(BaseHandler):

    @authenticated
    def POST(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        if not db_topic['opinion'].find_one({'_id': oid}):
            raise ResponseError(60)

        if db_user['approve'].is_opinion_approved(uid, oid):
            raise ResponseError(60)

        db_user['approve'].approve_opinion(uid, oid)

    @authenticated
    def DELETE(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        if not db_topic['opinion'].find_one({'_id': oid}):
            raise ResponseError(60)

        if not db_user['approve'].is_opinion_approved(uid, oid):
            raise ResponseError(60)

        db_user['approve'].unapprove_opinion(uid, oid)


class LikeCommentHandler(BaseHandler):

    @authenticated
    def POST(self, parent, coid):
        uid = self.current_user
        coid = self.to_objectid(coid)
        comment = db_topic['comment'].find_by_id(parent, coid)

        if not comment:
            raise ResponseError(70)

        if uid in comment['like']:
            raise ResponseError(75)

        db_topic['comment'].like_comment(parent, coid, uid)

