#-*- coding:utf-8 -*-

import log

from datetime import datetime

from tornado.escape import xhtml_escape

from models.topic import model as topic_model
from models.user import model as user_model
from helpers.base import DataProvider
from config.global_setting import PIC_URL

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Comment']


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

    # TODO fix 2 return
    def vote_proposal(self, tid, pid, uid):
        tid, pid, uid = map(self.to_objectid, [tid, pid, uid])

        if self.find_one({'_id': pid, 'tid': tid}):
            self._vote2proposal.create({'tid': tid, 'pid': pid, 'uid': uid})
            self.update({'_id': pid}, {'$inc': {'vnum': 1}}, w=1)
            return True

        return False

    def format(self, record, uid):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['auid'],
            'vote_num': record['vnum'],
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])
        result['is_voted'] =  self.is_voted({'uid': uid, 'pid': record['_id']})
        result['is_tz'] = True if self._topic.find_one({'_id': self.to_objectid(record['tid']), 'auid': self.to_objectid(record['auid'])}) else False

        simple_user = self.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result

    def get_proposals(self, tid, uid=None, skip=0, limit=10):
        spec = {'tid': self.to_objectid(tid)}
        sort = [('vnum', -1), ('ctime', 1)]
        proposals = self.get_all(spec, skip=skip, limit=limit, sort=sort)

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
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._format_time(record['ctime'])
        result['is_liked'] = True if unicode(uid) in record['like'] else False
        result['is_tz'] = True if self._topic.find_one({'_id': self.to_objectid(record['tid']), 'auid': self.to_objectid(record['auid'])}) else False

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
