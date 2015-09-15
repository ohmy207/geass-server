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


class PersonalHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 3),
        ]
    }

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
        self._data['publish_topics']['count'] = db_topic['topic'].find({'auid': uid}).count()
        self._data['publish_opinions']['count'] = db_opinion['opinion'].find({'auid': uid}).count()

        self._data['follow_topics']['data_list'] = db_user['follow'].get_follow_topics(
            uid=uid,
            skip=self._skip,
            limit=self._limit
        )

        self._data['publish_topics']['data_list'] = db_user['user'].get_user_topics(
            uid=uid,
            skip=self._skip,
            limit=self._limit
        )

        self._data['publish_opinions']['data_list'] = db_user['user'].get_user_opinions(
            uid=uid,
            skip=self._skip,
            limit=self._limit
        )


class PublishingHandler(BaseHandler):

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


class FollowingTopicHandler(BaseHandler):

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
            raise ResponseError(404)

        if db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(404)

        db_user['follow'].follow_topic(uid, tid)

    @authenticated
    def DELETE(self):
        uid = self.current_user
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if not db_user['follow'].is_topic_followed(uid, tid):
            raise ResponseError(404)

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
        topics = db_topic['topic'].get_all({'auid': uid}, skip=self._skip, limit=self._limit, sort=[('rtime', -1)])

        data_list = []
        for t in topics:
            tid = self.to_objectid(t['tid'])
            opinions = db_opinion['opinion'].get_all({'tid': tid}, skip=0, limit=2, sort=[('ctime', -1)])
            if not opinions:
                continue
            t['op_count'] = db_opinion['opinion'].find({'tid': tid}).count()
            t['op_authors'] = [op['author'] for op in opinions]
            data_list.append(t)

        self._data['data_list'] = data_list

    def do_votes(self):
        opinions = db_opinion['opinion'].get_all(
            {'auid': self.current_user, 'vnum': {'$gt': 0}},
            skip=self._skip,
            limit=self._limit,
            sort=[('vtime', -1)]
        )

        data_list = []
        for op in opinions:
            pid = self.to_objectid(op['pid'])
            # TODO Vote will not inherit Vote2Opinion
            votes = db_user['vote'].find({'pid': pid}, skip=0, limit=2, sort=[('ctime', -1)])
            op['vote_users'] = [db_user['user'].get_simple_user(v['uid'])['nickname'] for v in votes]
            op['title'] = db_topic['topic'].get_one({'_id': self.to_objectid(op['tid'])})['title']
            data_list.append(op)

        self._data['data_list'] = data_list

    def do_comments(self):
        comments = db_user['comment'].get_all(
            {'toauid': self.current_user},
            skip=self._skip,
            limit=self._limit,
            sort=[('ctime', -1)]
        )

        data_list = []
        for c in comments:
            c['target_content'] = db_user['comment'].get_one({'_id': self.to_objectid(c['tocoid'])})['content']
            data_list.append(c)

        self._data['data_list'] = data_list


# TODO restful standard
class VoteOpinionHandler(BaseHandler):

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

        if not db_opinion['opinion'].find_one({'_id': pid, 'tid': tid}):
            raise ResponseError(404)

        has_user_voted = db_user['vote'].has_user_voted(uid, tid)
        self.route(route, tid, pid, uid, has_user_voted)

    def do_vote(self, tid, pid, uid, has_user_voted):
        if has_user_voted:
            raise ResponseError(404)

        db_user['vote'].vote_opinion(tid, pid, uid)

    def do_unvote(self, tid, pid, uid, has_user_voted):
        if not db_user['vote'].is_opinion_voted(uid, pid):
            raise ResponseError(404)

        db_user['vote'].unvote_opinion(tid, pid, uid)

    def do_revote(self, tid, pid, uid, has_user_voted):
        if not has_user_voted or db_user['vote'].is_opinion_voted(uid, pid):
            raise ResponseError(404)

        voted_opinion = db_user['vote'].find_one({'tid': tid, 'uid': uid})
        if not voted_opinion:
            raise ResponseError(404)
        voted_pid = voted_opinion['pid']

        db_user['vote'].unvote_opinion(tid, voted_pid, uid)
        db_user['vote'].vote_opinion(tid, pid, uid)


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
        comment = db_user['comment'].find_one({'_id': coid})

        if not comment:
            raise ResponseError(404)

        if uid in comment['like']:
            raise ResponseError(404)

        db_user['comment'].update({'_id': coid}, {'$inc': {'lnum': 1}, '$push': {'like': uid}}, w=1)


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

    #@authenticated
    def GET(self, tid):
        data_list = db_user['comment'].get_comments(
            tid=tid,
            uid=self.current_user,
            skip=self._skip,
            limit=self._limit,
            sort = [('ctime', 1)],
        )

        self._data = {
            'data_list': data_list,
            'next_start': self._skip + self._limit
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
        data['tocoid'] = self.to_objectid(data['tocoid'])
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()
        data['istz'] = True if data['auid'] == topic['auid'] else False

        to_comment = db_user['comment'].find_one({'_id': data['tocoid']}) if data['tocoid'] else None
        data['toauid'] = to_comment['auid'] if to_comment else None

        coid = db_user['comment'].create(data)
        data['_id'] = coid

        self._data = db_user['comment'].callback(db_user['comment'].to_one_str(data))

