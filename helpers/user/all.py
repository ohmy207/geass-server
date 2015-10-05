#-*- coding:utf-8 -*-

import log

from datetime import datetime

from helpers.base import BaseHelper, UserHelper
from models.user import model as user_model
from helpers import topic as topic_helper
from config.global_setting import ANONYMOUS_USER

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User', 'Comment', 'Vote', 'Approve', 'Follow']


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


class Comment(BaseHelper):

    _user = User()

    _field_map = {
        'topics': 'tid',
        'opinions': 'oid',
    }

    _coll_map = {
        'topics': user_model.TopicComment(),
        'opinions': user_model.OpinionComment(),
    }

    def find_by_id(self, parent, coid):
        return self._coll_map[parent].find_one({'_id': coid})

    def format(self, record, uid):
        result = {
            'coid': record['_id'],
            'author_uid': record['uid'],
            'like_num': record['lnum'],
            'is_lz': record['islz'],
            'target': record['target'],
        }

        for k in record:
            if k in ['tid', 'oid']:
                result[k] = record[k]

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._simple_time(record['ctime'])
        result['is_liked'] = True if unicode(uid) in record['like'] else False

        if False and record['isanon']:
            result['author'] = ANONYMOUS_USER['nickname']
            result['avatar'] = ANONYMOUS_USER['avatar']
        else:
            simple_user = self._user.get_simple_user(record['uid'])
            result['author'] = simple_user['nickname']
            result['avatar'] = simple_user['avatar']

        if record['target']:
            if False and record['target']['isanon']:
                result['target']['author'] = ANONYMOUS_USER['nickname']
            else:
                to_user = self._user.get_simple_user(record['target']['uid'])
                result['target']['author'] = to_user['nickname']

        return result

    def get_comments(self, parent, parent_id, uid=None, skip=0, limit=5, sort=[('ctime', 1)]):
        coll = self._coll_map[parent]
        parent_id = coll.to_objectid(parent_id)
        spec = {self._field_map[parent]: parent_id}
        records = coll.get_all(spec, skip=skip, limit=limit, sort=sort)

        return [self.format(rd, uid) for rd in records]

    def add_comment(self, parent, parent_id, uid, content, tocoid=None, islz=False):
        parent_id, uid, tocoid= self.to_objectids(parent_id, uid, tocoid)
        key, coll = self._field_map[parent], self._coll_map[parent]
        doc = {
            key: parent_id,
            'uid': uid,
            'target': {},
            'content': content,
            'islz': islz,
            'ctime': datetime.now(),
        }
        target = coll.find_one({'_id': tocoid}) if tocoid else None
        if target:
            doc['target']['coid'] = target['_id']
            doc['target']['content'] = target['content']
            doc['target']['uid'] = target['uid']

        coid = coll.create(doc)
        doc['_id'] = coid
        return self.format(coll.to_one_str(doc), uid)

    def like_comment(self, parent, coid, uid):
        coid, uid = self.to_objectids(coid, uid)
        self._coll_map[parent].update(
            {'_id': coid},
            {'$inc': {'lnum': 1}, '$push': {'like': uid}},
            w=1
        )


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

