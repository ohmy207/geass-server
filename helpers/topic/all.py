#-*- coding:utf-8 -*-

import log

from datetime import datetime

from tornado.escape import xhtml_escape

from models.topic import model as topic_model
from models.user import model as user_model
from helpers.base import DataProvider
from config.global_setting import PIC_URL

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Comment', 'Follow', 'News']


class Topic(DataProvider, topic_model.Topic):

    _user = user_model.User()

    #@staticmethod
    def callback(self, record):
        result = {
            'tid':  record['_id'],
            'title': record['title'],
            'author_uid': record['auid'],
            'is_private': record['ispriv'],
            'is_anonymous': record['isanon'],
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        simple_user = self.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result


class Proposal(DataProvider, topic_model.Proposal):

    _user = user_model.User()
    _topic = topic_model.Topic()
    _vote2proposal = topic_model.Vote2Proposal()

    def is_voted(self, spec):
        spec = {k: self.to_objectid(v) for k, v in spec.items()}
        return True if self._vote2proposal.find_one(spec) else False

    #def vote_proposal(self, tid, pid, uid, method):
    #    tid, pid, uid = self.to_objectids(tid, pid, uid)
    #    collection_method = {
    #        'create': self._vote2proposal.create,
    #        'remove': self._vote2proposal.remove,
    #    }

    #    collection_method[method]({'tid': tid, 'pid': pid, 'uid': uid})
    #    self.update({'_id': pid}, {'$inc': {'vnum': 1 if method == 'create' else -1}}, w=1)

    def format(self, record, uid):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['auid'],
            'vote_num': record['vnum'],
            'is_tz': record['istz'],
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])
        result['is_voted'] =  self.is_voted({'uid': uid, 'pid': record['_id']})
        #result['is_tz'] = True if self._topic.find_one({'_id': self.to_objectid(record['tid']), 'auid': self.to_objectid(record['auid'])}) else False

        simple_user = self.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result

    def get_proposals(self, tid, uid=None, skip=0, limit=5, first=0, sort=[('vnum', -1), ('ctime', 1)]):
        spec = {'tid': self.to_objectid(tid), 'istz': False}
        #sort = [('vnum', -1), ('ctime', 1)]
        proposals = self.get_all(spec, skip=skip, limit=limit, sort=sort)

        if first == 1:
            spec['istz'] = True
            proposals.extend(self.get_all(spec, skip=skip, limit=limit, sort=sort))

        return [self.format(p, uid) for p in proposals if p]


class Comment(DataProvider, topic_model.Comment):

    _user = user_model.User()
    _topic = topic_model.Topic()

    def format(self, record, uid):
        result = {
            'tid': record['tid'],
            'coid': record['_id'],
            'author_uid': record['auid'],
            'like_num': record['lnum'],
            'is_tz': record['istz'],
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._simple_time(record['ctime'])
        result['is_liked'] = True if unicode(uid) in record['like'] else False
        #result['is_tz'] = True if self._topic.find_one({'_id': self.to_objectid(record['tid']), 'auid': self.to_objectid(record['auid'])}) else False

        simple_user = self.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        to_user = self._user.get_one({'_id': self.to_objectid(record['toauid'])})
        result['to_author'] = to_user['nickname'] if to_user else None

        return result

    def get_comments(self, tid, uid=None, skip=0, limit=10, order=1):
        spec = {'tid': self.to_objectid(tid)}
        sort = [('ctime', order)]
        comments = self.get_all(spec, skip=skip, limit=limit, sort=sort)

        return [self.format(co, uid) for co in comments]


class Follow(DataProvider):

    _topic = Topic()
    _user2topic = topic_model.User2Topic()

    def is_followed(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        return True if self._user2topic.find_one({'uid': uid, 'tid': tid}) else False

    def follow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._user2topic.create({'tid': tid, 'uid': uid, 'ctime': datetime.now()})

    def unfollow_topic(self, uid, tid):
        uid, tid = self.to_objectids(uid, tid)
        self._user2topic.remove({'tid': tid, 'uid': uid})

    def get_follows(self, uid, skip=0, limit=5, order=-1):
        #uid = self.to_objectid(uid)
        sort = [('ctime', order)]
        follows = self._user2topic.find({'uid': uid}, skip=skip, limit=limit, sort=sort)

        topics = []
        for f in follows:
            topic = self._topic.get_one({'_id': f['tid']})
            if topic:
                topics.append(topic)

        return topics

    def get_follows_count(self, uid):
        return self._user2topic.find({'uid': uid}).count()


class News(DataProvider):

    _topic = Topic()
    _proposal = Proposal()
    _comment = Comment()
    _vote2proposal = topic_model.Vote2Proposal()

    def get_topics(self, uid, skip=0, limit=5):
        topics = self._topic.get_all({'auid': uid}, skip=skip, limit=limit, sort=[('ptime', -1)])
        result_list = []

        for t in topics:
            tid = self._topic.to_objectid(t['tid'])
            proposals = self._proposal.get_proposals(tid=tid, skip=0, limit=2, sort=[('ctime', -1)])
            if not proposals:
                continue

            t['p_count'] = self._proposal.find({'tid': tid}).count()
            t['p_authors'] = [p['author'] for p in proposals]
            result_list.append(t)

        return result_list

    def get_votes(self, uid, skip=0, limit=5):
        proposals = self._proposal.get_all({'auid': uid, 'vnum': {'$gt': 0}}, skip=skip, limit=limit, sort=[('vtime', -1)])
        result_list = []

        for p in proposals:
            p = self._proposal.format(p, None)
            #if not p['vote_num']:
            #    continue

            pid = self._topic.to_objectid(p['pid'])
            votes = self._vote2proposal.find({'pid': pid}, skip=0, limit=2, sort=[('ctime', -1)])
            p['vote_users'] = [self._user.get_one({'_id': v['uid']})['nickname'] for v in votes]
            p['title'] = self._topic.get_one({'_id': self._topic.to_objectid(p['tid'])})['title']
            result_list.append(p)

        return result_list

    def get_comments(self, uid, skip=0, limit=5):
        comments = self._comment.get_all({'toauid': uid}, skip=skip, limit=limit, sort=[('ctime', -1)])
        result_list = []

        for c in comments:
            c = self._comment.format(c, None)
            c['target_content'] = self._comment.get_one({'_id': self._comment.to_objectid(c['coid'])})['content']
            result_list.append(c)

        return result_list
