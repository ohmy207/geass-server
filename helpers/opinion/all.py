#-*- coding:utf-8 -*-

import log

from models.user import model as user_model
from models.opinion import model as opinion_model
from helpers.base import BaseHelper, UserHelper
from config.global_setting import PIC_URL

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Opinion']


class Opinion(BaseHelper, opinion_model.Opinion):

    _user = UserHelper()
    _vote2opinion = user_model.Vote2Opinion()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['auid'],
            'vote_num': record['vnum'],
            'is_tz': record['istz'],
        }

        result['content'] = Opinion.xhtml_escape(record['content'])
        result['f_created_time'] = Opinion._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        simple_user = Opinion._user.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result

    def _is_voted(self, spec):
        spec = {k: self.to_objectid(v) for k, v in spec.items()}
        return True if self._vote2opinion.find_one(spec) else False

    def is_opinion_voted(self, uid, pid):
        return self._is_voted({'uid': uid, 'pid': pid})

    def has_user_voted(self, uid, tid):
        return self._is_voted({'uid': uid, 'tid': tid})

    #def get_opinions(self, tid, uid=None, skip=0, limit=5, first=0, sort=[('vnum', -1), ('ctime', 1)]):
    #    spec = {'tid': self.to_objectid(tid), 'istz': False}
    #    #sort = [('vnum', -1), ('ctime', 1)]
    #    opinions = self.get_all(spec, skip=skip, limit=limit, sort=sort)

    #    if first == 1:
    #        spec['istz'] = True
    #        opinions.extend(self.get_all(spec, skip=skip, limit=limit, sort=sort))

    #    return [self.format(p, uid) for p in opinions if p]

