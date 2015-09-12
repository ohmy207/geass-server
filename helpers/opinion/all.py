#-*- coding:utf-8 -*-

import log

from datetime import datetime

from tornado.escape import xhtml_escape

from models.topic import model as topic_model
from models.user import model as user_model
from helpers.base import DataProvider
from config.global_setting import PIC_URL

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Opinion']


class Opinion(DataProvider, topic_model.Opinion):

    _user = user_model.User()
    _topic = topic_model.Topic()
    _vote2opinion = topic_model.Vote2Opinion()

    def is_voted(self, spec):
        spec = {k: self.to_objectid(v) for k, v in spec.items()}
        return True if self._vote2opinion.find_one(spec) else False

    #def vote_opinion(self, tid, pid, uid, method):
    #    tid, pid, uid = self.to_objectids(tid, pid, uid)
    #    collection_method = {
    #        'create': self._vote2opinion.create,
    #        'remove': self._vote2opinion.remove,
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

    def get_opinions(self, tid, uid=None, skip=0, limit=5, first=0, sort=[('vnum', -1), ('ctime', 1)]):
        spec = {'tid': self.to_objectid(tid), 'istz': False}
        #sort = [('vnum', -1), ('ctime', 1)]
        opinions = self.get_all(spec, skip=skip, limit=limit, sort=sort)

        if first == 1:
            spec['istz'] = True
            opinions.extend(self.get_all(spec, skip=skip, limit=limit, sort=sort))

        return [self.format(p, uid) for p in opinions if p]


