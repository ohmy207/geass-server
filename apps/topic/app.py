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

        topic = db_topic['topic'].get_one({'_id': tid})
        opinions = db_topic['opinion'].get_opinions(tid, uid=uid, skip=self._skip, limit=self._limit, first=1)
        has_voted = db_topic['opinion'].is_voted({'tid': tid, 'uid': uid})

        self._data = {
            'topic': topic,
            'dataList': opinions,
            'nextStart': self._skip + self._limit,
            'has_voted': has_voted,
        }


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
        sort = [('ctime', -1)]

        user = db_user['user'].get_one({'_id': self.current_user})
        follow_topics = db_topic['follow'].get_follows(self.current_user, skip=self._skip, limit=self._limit)
        publish_topics = db_topic['topic'].get_all({'auid': self.current_user}, skip=self._skip, limit=self._limit, sort=sort)
        follow_topics_count = db_topic['follow'].get_follows_count(self.current_user)
        publish_topics_count = db_topic['topic'].find({'auid': self.current_user}).count()

        self._data = {
            'user': user,
            'news': {},
            'follow': {'data_list': follow_topics, 'count': follow_topics_count},
            'publish': {'data_list': publish_topics, 'count': publish_topics_count},
            #'nextStart': self._skip + self._limit,
        }


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
        sort = [('ctime', -1)]

        self._data = {
            'nextStart': self._skip + self._limit,
        }

        self.route(route, sort)

    def do_topics(self, sort):
        data_list = db_topic['topic'].get_all({'auid': self.current_user}, skip=self._skip, limit=self._limit, sort=sort)
        self._data['dataList'] = data_list

    def do_opinions(self, sort):
        data_list = db_topic['opinion'].get_all({'auid': self.current_user}, skip=self._skip, limit=self._limit, sort=sort)
        self._data['dataList'] = data_list


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
    def GET(self, route):
        sort = [('ctime', -1)]

        self._data = {
            'nextStart': self._skip + self._limit,
        }

        self.route(route, sort)

    def do_topics(self, sort):
        data_list = db_topic['follow'].get_follows(self.current_user, skip=self._skip, limit=self._limit)
        self._data['dataList'] = data_list

    @authenticated
    def POST(self, route):
        uid = self.current_user
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if db_topic['follow'].is_followed(uid, tid):
            raise ResponseError(404)

        db_topic['follow'].follow_topic(uid, tid)

    @authenticated
    def DELETE(self, route):
        uid = self.current_user
        tid = self.to_objectid(self._params['tid'])

        if not db_topic['topic'].find_one({'_id': tid}):
            raise ResponseError(404)

        if not db_topic['follow'].is_followed(uid, tid):
            raise ResponseError(404)

        db_topic['follow'].unfollow_topic(uid, tid)


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
            'nextStart': self._skip + self._limit,
        }

        self.route(route)

    def do_topics(self):
        data_list = db_topic['news'].get_topics(self.current_user, skip=self._skip, limit=self._limit)
        self._data['dataList'] = data_list

    def do_votes(self):
        data_list = db_topic['news'].get_votes(self.current_user, skip=self._skip, limit=self._limit)
        self._data['dataList'] = data_list

    def do_comments(self):
        data_list = db_topic['news'].get_comments(self.current_user, skip=self._skip, limit=self._limit)
        self._data['dataList'] = data_list


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
        # TODO tz default
        opinions = db_topic['opinion'].get_opinions(tid, uid=self.current_user, skip=self._skip, limit=self._limit)

        self._data = {
            'dataList': opinions,
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

        pid = db_topic['opinion'].create(data)
        data['_id'] = pid

        self._data = db_topic['opinion'].format(db_topic['opinion'].to_one_str(data), data['auid'])


class DetailOpinionHandler(BaseHandler):

    #@authenticated
    def GET(self, pid):
        data = db_topic['opinion'].get_one(self.to_objectid(pid))
        data = db_topic['opinion'].format(data, self.current_user)

        data['title'] = db_topic['topic'].find_one({'_id': self.to_objectid(data['tid'])}, {'title': 1})['title']
        has_voted = db_topic['opinion'].is_voted({'tid': data['tid'], 'uid': self.current_user})

        self._data = {
            'opinion': data,
            'has_voted': has_voted,
        }


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

        if not db_topic['opinion'].find_one({'_id': pid, 'tid': tid}):
            raise ResponseError(404)

        self.route(route, tid, pid, uid)

    def do_vote(self, tid, pid, uid):
        if db_topic['opinion'].is_voted({'uid': uid, 'tid': tid}):
            raise ResponseError(404)

        db_topic['opinion']._vote2opinion.create({'tid': tid, 'pid': pid, 'uid': uid, 'ctime': datetime.now()})
        db_topic['opinion'].update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)

    def do_unvote(self, tid, pid, uid):
        if not db_topic['opinion'].is_voted({'uid': uid, 'tid': tid}):
            raise ResponseError(404)

        db_topic['opinion']._vote2opinion.remove({'tid': tid, 'pid': pid, 'uid': uid})
        db_topic['opinion'].update({'_id': pid}, {'$inc': {'vnum': -1}}, w=1)

    def do_revote(self, tid, pid, uid):
        if db_topic['opinion'].is_voted({'uid': uid, 'tid': tid, 'pid': pid}):
            raise ResponseError(404)

        old_opinion = db_topic['opinion']._vote2opinion.find_one({'tid': tid, 'uid': uid})
        if not old_opinion:
            raise ResponseError(404)
        old_pid = old_opinion['pid']

        db_topic['opinion']._vote2opinion.remove({'tid': tid, 'uid': uid})
        db_topic['opinion'].update({'_id': old_pid}, {'$inc': {'vnum': -1}}, w=1)

        db_topic['opinion']._vote2opinion.create({'tid': tid, 'pid': pid, 'uid': uid, 'ctime': datetime.now()})
        db_topic['opinion'].update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)


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
        data_list = db_topic['comment'].get_comments(self.to_objectid(tid), uid=self.current_user, skip=self._skip, limit=self._limit)

        self._data = {
            'dataList': data_list,
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
        data['tocoid'] = self.to_objectid(data['tocoid'])
        data['auid'] = self.current_user
        data['ctime'] = datetime.now()
        data['istz'] = True if data['auid'] == topic['auid'] else False

        to_comment = db_topic['comment'].find_one({'_id': data['tocoid']}, {'auid': 1}) if data['tocoid'] else None
        data['toauid'] = to_comment['auid'] if to_comment else None

        coid = db_topic['comment'].create(data)
        data['_id'] = coid

        self._data = db_topic['comment'].format(db_topic['comment'].to_one_str(data), data['auid'])


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

