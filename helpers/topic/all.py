#-*- coding:utf-8 -*-

import log

from models.topic import model as topic_model
from helpers.base import UserHelper
from config.global_setting import PIC_URL

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Follow']


class Topic(BaseHelper, topic_model.Topic):

    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid':  record['_id'],
            'title': record['title'],
            'author_uid': record['auid'],
            'is_private': record['ispriv'],
            'is_anonymous': record['isanon'],
        }

        result['content'] = Topic.xhtml_escape(record['content'])
        result['f_created_time'] = Topic._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        simple_user = Topic._user.get_simple_user(record['auid'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result


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

