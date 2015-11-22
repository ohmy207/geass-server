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
        has_new_notice = True if db_user['notice'].find_one(
            {'uid': uid, 'isread': False}) else False

        self._data = {
            'user': db_user['user'].get_one({'_id': uid}),
            'has_new_notice': has_new_notice,
            'follow_topics': {},
            'publish_topics': {},
            'publish_opinions': {},
        }
        self._data['follow_topics']['count'] = db_user[
            'follow'].get_follows_count(uid)
        self._data['publish_topics']['count'] = db_topic[
            'topic'].find({'uid': uid}).count()
        self._data['publish_opinions']['count'] = db_topic[
            'opinion'].find({'uid': uid}).count()

        self._data['follow_topics']['data_list'] = db_user[
            'follow'].get_follow_topics(uid=uid, skip=0, limit=3)
        self._data['publish_topics']['data_list'] = db_user[
            'user'].get_user_topics(uid=uid, skip=0, limit=3)
        self._data['publish_opinions']['data_list'] = db_user[
            'user'].get_user_opinions(uid=uid, skip=0, limit=3)


class UserSourceHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 15),
        ]
    }

    @authenticated
    def GET(self, route):
        self._data = {
            'next_start': self._skip + self._limit,
        }

        self.route(route)

    def do_topics(self):
        self._data['data_list'] = db_user['user'].get_user_topics(
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit,
        )

    def do_opinions(self):
        self._data['data_list'] = db_user['user'].get_user_opinions(
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit,
        )

    def do_following(self):
        self._data['data_list'] = db_user['follow'].get_follow_topics(
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit
        )


class FollowTopicHandler(BaseHandler):

    @authenticated
    def POST(self, tid):
        uid = self.current_user
        tid = self.to_objectid(tid)

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(51)

        db_user['follow'].follow_topic(uid, tid)

    @authenticated
    def DELETE(self, tid):
        uid = self.current_user
        tid = self.to_objectid(tid)

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if not db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(52)

        db_user['follow'].unfollow_topic(uid, tid)


class NotificationHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 15),
            ('type', basestring, None),
        ]
    }

    @authenticated
    def GET(self):
        uid = self.current_user
        filter_type = self._params['type']

        data_list = db_user['notice'].get_notices(
            uid, filter_type, self._skip, self._limit)

        self._data = {
            'data_list': data_list,
            'next_start': self._skip + self._limit,
        }

        if self._skip == 0:
            db_user['notice'].check_all_notices(uid, filter_type)
            self._data['has_new_support'] = True if db_user['notice'].find_one(
                {'uid': uid, 'isread': False, 'action': {'$in': [7, 8]}}) else False


# TODO code repeat
class VoteProposalHandler(BaseHandler):

    @authenticated
    def POST(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(404)

        tid = proposal['tid']
        if db_user['vote'].has_user_voted(uid, tid):
            raise ResponseError(91)

        db_user['vote'].vote_proposal(tid, pid, uid)

    @authenticated
    def DELETE(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(404)

        if not db_user['vote'].is_proposal_voted(uid, pid):
            raise ResponseError(92)

        db_user['vote'].unvote_proposal(proposal['tid'], pid, uid)

    def PATCH(self, pid):
        uid = self.current_user
        pid = self.to_objectid(pid)
        proposal = db_topic['proposal'].find_one({'_id': pid})

        if not proposal:
            raise ResponseError(404)

        tid = proposal['tid']
        if not db_user['vote'].has_user_voted(uid, tid):
            raise ResponseError(92)

        if db_user['vote'].is_proposal_voted(uid, pid):
            raise ResponseError(91)

        voted_proposal = db_user['vote'].find_one({'tid': tid, 'uid': uid})
        if not voted_proposal:
            raise ResponseError(404)

        db_user['vote'].unvote_proposal(tid, voted_proposal['pid'], uid)
        db_user['vote'].vote_proposal(tid, pid, uid)


class ApproveOpinionHandler(BaseHandler):

    @authenticated
    def POST(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        if not db_topic['opinion'].find_one({'_id': oid}):
            raise ResponseError(404)

        if db_user['approve'].is_opinion_approved(uid, oid):
            raise ResponseError(72)

        db_user['approve'].approve_opinion(uid, oid)
        db_user['notice'].update_notice(oid, 7)

    @authenticated
    def DELETE(self, oid):
        uid = self.current_user
        oid = self.to_objectid(oid)

        if not db_topic['opinion'].find_one({'_id': oid}):
            raise ResponseError(404)

        if not db_user['approve'].is_opinion_approved(uid, oid):
            raise ResponseError(73)

        db_user['approve'].unapprove_opinion(uid, oid)


class LikeCommentHandler(BaseHandler):

    @authenticated
    def POST(self, parent, coid):
        uid = self.current_user
        coid = self.to_objectid(coid)
        comment = db_topic['comment'].find_by_id(parent, coid)

        if not comment:
            raise ResponseError(404)

        if uid in comment['like']:
            raise ResponseError(81)

        db_topic['comment'].like_comment(parent, coid, uid)
