#-*- coding:utf-8 -*-

import log

from datetime import datetime

from helpers.base import BaseHelper, UserHelper
from models.user import model as user_model
from helpers import topic as topic_helper
from config.global_setting import ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User', 'Vote', 'Approve', 'Follow']


class User(UserHelper):

    _topic = topic_helper['topic']
    _opinion = topic_helper['opinion']

    def get_user_topics(self, uid, skip, limit, sort=[('ctime', -1)]):
        spec = {'uid': self.to_objectid(uid)}
        return self._topic.get_all(
            spec,
            skip=skip,
            limit=limit,
            sort=sort
        )

    def get_user_opinions(self, uid, skip, limit, sort=[('ctime', -1)]):
        spec = {'uid': self.to_objectid(uid)}
        opinions = self._opinion.get_all(
            spec,
            skip=skip,
            limit=limit,
            sort=sort
        )

        for op in opinions:
            topic = self._topic.find_one(
                {'_id': self.to_objectid(op['tid'])},
                {'title': 1}
            )
            op['title'] = topic['title']

        return opinions


class Vote(BaseHelper, user_model.Vote2Proposal):

    _proposal = topic_helper['proposal']

    def _is_existed(self, spec):
        spec = {k: self.to_objectid(v) for k, v in spec.items()}
        return True if self.find_one(spec) else False

    def is_proposal_voted(self, uid, pid):
        return self._is_existed({'uid': uid, 'pid': pid})

    def has_user_voted(self, uid, tid):
        return self._is_existed({'uid': uid, 'tid': tid})

    def format_proposals(self, uid, records):
        for r in records:
            r['is_voted'] = self.is_proposal_voted(uid, r['pid'])
        return records

    def vote_proposal(self, tid, pid, uid):
        tid, pid, uid = self.to_objectids(tid, pid, uid)
        self.create({'tid': tid, 'pid': pid, 'uid': uid, 'ctime': datetime.now()})
        self._proposal.update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)

    def unvote_proposal(self, tid, pid, uid):
        tid, pid, uid = self.to_objectids(tid, pid, uid)
        self.remove({'tid': tid, 'pid': pid, 'uid': uid})
        self._proposal.update({'_id': pid}, {'$inc': {'vnum': -1}}, w=1)


class Approve(BaseHelper, user_model.Approve2Opinion):

    _opinion = topic_helper['opinion']

    def is_opinion_approved(self, uid, oid):
        uid, oid = self.to_objectids(uid, oid)
        return True if self.find_one({'uid': uid, 'oid': oid}) else False

    def format_opinions(self, uid, records):
        for r in records:
            r['is_approved'] = self.is_opinion_approved(uid, r['oid'])
        return records

    def approve_opinion(self, uid, oid):
        uid, oid = self.to_objectids(uid, oid)
        self.create({'oid': oid, 'uid': uid, 'ctime': datetime.now()})
        self._opinion.update({'_id': oid}, {'$inc': {'anum': 1}}, w=1)

    def unapprove_opinion(self, uid, oid):
        uid, oid = self.to_objectids(uid, oid)
        self.remove({'oid': oid, 'uid': uid})
        self._opinion.update({'_id': oid}, {'$inc': {'anum': -1}}, w=1)


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

