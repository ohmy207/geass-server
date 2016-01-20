# -*- coding:utf-8 -*-

from datetime import datetime

import log
from helpers import topic as topic_helper
from helpers.base import BaseHelper, UserHelper
from models.topic import model as topic_model
from models.user import model as user_model

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User', 'Vote', 'Approve', 'Follow', 'Notice']


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
            op['topic_title'] = topic['title']

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
        self.create(
            {'tid': tid, 'pid': pid, 'uid': uid, 'ctime': datetime.now()})
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
        return True if self._follow2topic.find_one(
            {'uid': uid, 'tid': tid}) else False

    def get_follow_topics(self, uid, skip, limit, sort=[('ctime', -1)]):
        follow_topics = self._follow2topic.find(
            {'uid': uid}, skip=skip, limit=limit, sort=sort)
        return [self._topic.get_one({'_id': f['tid']})
                for f in follow_topics if follow_topics and f['tid']]

    def follow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._follow2topic.create(
            {'tid': tid, 'uid': uid, 'ctime': datetime.now()})

    def unfollow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._follow2topic.remove({'tid': tid, 'uid': uid})

    def get_follows_count(self, uid):
        return self._follow2topic.find({'uid': uid}).count()


class Notice(BaseHelper, user_model.Notice):

    _user = User()
    _topic = topic_helper['topic']
    _topicomment = topic_model.TopicComment()
    _opinioncomment = topic_model.OpinionComment()

    _child_map = {
        1: topic_helper['proposal'],
        2: topic_helper['opinion'],
        3: _topicomment,
        4: _topicomment,
        5: _opinioncomment,
        6: _opinioncomment,
        7: user_model.Approve2Opinion(),
        8: user_model.Vote2Proposal(),
        9: topic_model.TopicEditLog(),
        10: topic_model.ProposalEditLog(),
    }

    _parent_map = {
        1: _topic,
        2: _topic,
        3: _topic,
        4: _topic,
        5: topic_helper['opinion'],
        6: topic_helper['opinion'],
        7: topic_helper['opinion'],
        8: topic_helper['proposal'],
        9: _topic,
        10: topic_helper['proposal'],
    }

    def update_notice(self, parent_id, action, uid=None):
        parent_id, uid = self.to_objectids(parent_id, uid)
        uid = uid if action in [4, 6] else\
            self._parent_map[action].find_one({'_id': parent_id})['uid']

        doc = {
            'uid': uid,
            'paid': parent_id,
            'action': action,
        }
        notice = self.find_one(doc)
        notice_id = self.create(doc) if not notice else notice['_id']
        self.update(
            {'_id': notice_id}, {'$set': {'isread': False, 'ctime': datetime.now()}})

    def get_notices(self, uid, filter_type, skip, limit):
        spec = {'uid': uid,
            'action': {'$in': [7, 8]} if filter_type == 'support' else {'$nin': [7, 8]}}
        notices = self.find(spec, limit=limit, skip=skip, sort=[('ctime', -1)])

        result_list = []
        for notice in notices:
            action = notice['action']
            result = self._parent_map[action].get_one({'_id': notice['paid']})

            key = 'pid' if action in [8, 10] else 'oid' if action in [5, 6, 7] else 'tid'
            uids = self._child_map[action].find(
                {key: self.to_objectid(result[key])}, sort=[('ctime', -1)]).distinct('uid')

            if not uids:
                continue

            if action not in [1, 2, 3, 4, 9]:
                result['topic_title'] = self._topic.find_one(
                    {'_id': self.to_objectid(result['tid'])}, {'title': 1})['title']

            result['action'] = action
            result['isread'] = notice['isread']
            result['count'] = len(uids)
            result['senders'] = [
                self._user.get_simple_user(u)['nickname'] for u in uids[:2]]

            result_list.append(result)

        return result_list

    def check_all_notices(self, uid, filter_type):
        spec = {'uid': uid, 'isread': False,
                'action': {'$in': [7, 8]} if filter_type == 'support' else {'$nin': [7, 8]}}

        if not self.find_one(spec):
            return

        self.update(spec, {'$set': {'isread': True}}, multi=True)
