#-*- coding:utf-8 -*-

import log

from datetime import datetime

from helpers.base import BaseHelper, UserHelper
from models.user import model as user_model
from helpers import topic as topic_helper
from helpers import opinion as opinion_helper

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User', 'Comment', 'Vote', 'Follow']


class User(UserHelper):

    _topic = topic_helper['topic']
    _opinion = opinion_helper['opinion']

    def get_user_topics(self, uid, skip, limit, sort=[('ctime', -1)]):
        spec = {'auid': self.to_objectid(uid)}
        return self._topic.get_all(
            spec,
            skip=skip,
            limit=limit,
            sort=sort
        )

    def get_user_opinions(self, uid, skip, limit, sort=[('ctime', -1)]):
        spec = {'auid': self.to_objectid(uid)}
        return self._opinion.get_all(
            spec,
            skip=skip,
            limit=limit,
            sort=sort
        )


class Comment(BaseHelper, user_model.Comment):

    _user = User()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['pid'],
            'coid': record['_id'],
            'author_uid': record['auid'],
            'like_num': record['lnum'],
            'is_tz': record['istz'],
            'tocoid': record['tocoid'],
            #'is_liked': False,
        }

        result['content'] = Comment.xhtml_escape(record['content'])
        result['f_created_time'] = Comment._simple_time(record['ctime'])

        simple_user = Comment._user.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        to_user = Comment._user.get_simple_user(record['toauid'])
        result['to_author'] = to_user['nickname']

        return result

    def get_comments(self, tid, pid=None, uid=None, skip=0, limit=5, sort=[('ctime', 1)]):
        spec = {
            'tid': self.to_objectid(tid),
            'pid': self.to_objectid(pid),
        }
        records = self.find(
            spec=spec,
            skip=skip,
            limit=limit,
            sort=sort,
        )

        result_list = []
        for record in records:
            is_liked = True if self.to_objectid(uid) in record['like'] else False
            result = self.callback(self.to_one_str(record))
            result['is_liked'] = is_liked
            result_list.append(result)

        return result_list


# TODO Vote will not inherit Vote2Opinion
class Vote(BaseHelper, user_model.Vote2Opinion):

    _opinion = opinion_helper['opinion']
    #_vote2opinion = user_model.Vote2Opinion()

    def _is_voted(self, spec):
        spec = {k: self.to_objectid(v) for k, v in spec.items()}
        return True if self.find_one(spec) else False

    def is_opinion_voted(self, uid, pid):
        return self._is_voted({'uid': uid, 'pid': pid})

    def has_user_voted(self, uid, tid):
        return self._is_voted({'uid': uid, 'tid': tid})

    def format_opinions(self, uid, records):
        for r in records:
            r['is_voted'] = self.is_opinion_voted(uid, r['pid'])
        return records

    # TODO vote_opinion unvote_opinion
    def vote_opinion(self, tid, pid, uid):
        tid, pid, uid = self.to_objectids(tid, pid, uid)
        self.create({'tid': tid, 'pid': pid, 'uid': uid, 'ctime': datetime.now()})
        self._opinion.update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)

    def unvote_opinion(self, tid, pid, uid):
        tid, pid, uid = self.to_objectids(tid, pid, uid)
        self.remove({'tid': tid, 'pid': pid, 'uid': uid})
        self._opinion.update({'_id': pid}, {'$inc': {'vnum': -1}}, w=1)


class Follow(BaseHelper):

    _topic = topic_helper['topic']
    _follow2topic = user_model.Follow2Topic()

    def is_topic_followed(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        return True if self._follow2topic.find_one({'uid': uid, 'tid': tid}) else False

    def get_follow_topics(self, uid, skip, limit, sort=[('ctime', -1)]):
        follow_topics = self._follow2topic.find({'uid': uid}, skip=skip, limit=limit, sort=sort)
        return [self._topic.get_one({'_id': f['tid']}) for f in follow_topics if follow_topics and f['tid']]

    def follow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._follow2topic.create({'tid': tid, 'uid': uid, 'ctime': datetime.now()})

    def unfollow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._follow2topic.remove({'tid': tid, 'uid': uid})

    def get_follows_count(self, uid):
        return self._follow2topic.find({'uid': uid}).count()

