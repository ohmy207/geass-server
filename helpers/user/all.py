#-*- coding:utf-8 -*-

import log

from helpers.base import BaseHelper, UserHelper
from models.user import model as user_model

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User']


class User(UserHelper):
    pass


class Comment(BaseHelper, user_model.Comment):

    _user = User()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'coid': record['_id'],
            'author_uid': record['auid'],
            'like_num': record['lnum'],
            'is_tz': record['istz'],
            'tocoid': record['tocoid'],
        }

        result['content'] = Comment.xhtml_escape(record['content'])
        result['f_created_time'] = Comment._simple_time(record['ctime'])
        #result['is_liked'] = True if unicode(uid) in record['like'] else False

        simple_user = Comment._user.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        to_user = Comment._user.get_simple_user(record['toauid'])
        result['to_author'] = to_user['nickname']

        return result

    def is_comment_liked(self, uid, record):
        return True if unicode(uid) in record['like'] else False

    #def get_comments(self, tid, uid=None, skip=0, limit=10, order=1):
    #    spec = {'tid': self.to_objectid(tid)}
    #    sort = [('ctime', order)]
    #    comments = self.get_all(spec, skip=skip, limit=limit, sort=sort)

    #    return [self.format(co, uid) for co in comments]


class News(object):

    _comment = Comment()
    _vote2opinion = opinion_model.Vote2Opinion()

    def get_reply_topics(self, uid, skip, limit):
        topics = self._topic.get_all({'auid': uid}, skip=skip, limit=limit, sort=[('ptime', -1)])
        result_list = []

        for t in topics:
            tid = self._topic.to_objectid(t['tid'])
            opinions = self._opinion.get_opinions(tid=tid, skip=0, limit=2, sort=[('ctime', -1)])
            if not opinions:
                continue

            t['p_count'] = self._opinion.find({'tid': tid}).count()
            t['p_authors'] = [p['author'] for p in opinions]
            result_list.append(t)

        return result_list

    def get_votes(self, uid, skip=0, limit=5):
        opinions = self._opinion.get_all({'auid': uid, 'vnum': {'$gt': 0}}, skip=skip, limit=limit, sort=[('vtime', -1)])
        result_list = []

        for p in opinions:
            p = self._opinion.format(p, None)
            #if not p['vote_num']:
            #    continue

            pid = self._topic.to_objectid(p['pid'])
            votes = self._vote2opinion.find({'pid': pid}, skip=0, limit=2, sort=[('ctime', -1)])
            p['vote_users'] = [self._user.get_one({'_id': v['uid']})['nickname'] for v in votes]
            p['title'] = self._topic.get_one({'_id': self._topic.to_objectid(p['tid'])})['title']
            result_list.append(p)

        return result_list

    def get_comments(self, uid, skip=0, limit=5):
        comments = self._comment.get_all({'toauid': uid}, skip=skip, limit=limit, sort=[('ctime', -1)])
        result_list = []

        for c in comments:
            c = self._comment.format(c, None)
            c['target_content'] = self._comment.get_one({'_id': self._comment.to_objectid(c['tocoid'])})['content']
            result_list.append(c)

        return result_list
