# -*- coding:utf-8 -*-

from datetime import datetime

import log
from config.global_setting import PIC_URL
from helpers.base import BaseHelper, UserHelper
from models.topic import model as topic_model

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Opinion', 'Comment', 'PublicEdit']


class Topic(BaseHelper, topic_model.Topic):

    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['_id'],
            'title': record['title'],
            'author_uid': record['uid'],
            'is_anonymous': record['isanon'],
        }

        result['content'] = Topic.xhtml_escape(record['content'])
        result['f_created_time'] = Topic._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        return result


class Proposal(BaseHelper, topic_model.Proposal):

    _topic = Topic()
    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'pid': record['_id'],
            'author_uid': record['uid'],
            'title': record['title'],
            'vote_num': record['vnum'],
            'is_voted': False,
        }

        result['content'] = Opinion.xhtml_escape(record['content'])
        result['f_created_time'] = Opinion._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        return result


class Opinion(BaseHelper, topic_model.Opinion):

    _proposal = Proposal()
    _user = UserHelper()

    @staticmethod
    def callback(record):
        result = {
            'tid': record['tid'],
            'oid': record['_id'],
            'author_uid': record['uid'],
            'approve_num': record['anum'],
            'is_anonymous': record['isanon'],
            'is_approved': False,
        }

        result['content'] = Opinion.xhtml_escape(record['content'])
        result['f_created_time'] = Opinion._format_time(record['ctime'])
        result['picture_urls'] = map(PIC_URL['img'], record['pickeys'])

        simple_user = Opinion._user.get_simple_user(
            record['uid'], record['isanon'])
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        return result


class Comment(BaseHelper):

    _topic = Topic()
    _opinion = Opinion()
    _user = UserHelper()

    _field_map = {
        'topics': 'tid',
        'opinions': 'oid',
    }

    _coll_map = {
        'topics': topic_model.TopicComment(),
        'opinions': topic_model.OpinionComment(),
    }

    def find_by_id(self, parent, coid):
        return self._coll_map[parent].find_one({'_id': coid})

    def get_comments_count(self, parent, parent_id):
        coll = self._coll_map[parent]
        parent_id = coll.to_objectid(parent_id)
        spec = {self._field_map[parent]: parent_id}
        return self._coll_map[parent].find(spec).count()

    def format(self, record, uid):
        result = {
            'coid': record['_id'],
            'author_uid': record['uid'],
            'like_num': record['lnum'],
            'is_lz': record['islz'],
            'target': {},
        }

        result['content'] = self.xhtml_escape(record['content'])
        result['f_created_time'] = self._simple_time(record['ctime'])
        result['is_liked'] = True if unicode(uid) in record['like'] else False

        parent_key = (set(['tid', 'oid']) & set(record.keys())).pop()
        parent_id = result[parent_key] = record[parent_key]
        parent_coll = self._topic if parent_key == 'tid' else self._opinion

        is_anon = parent_coll.find_one(
            {'_id': parent_coll.to_objectid(parent_id)})['isanon'] if result['is_lz'] else False

        simple_user = self._user.get_simple_user(record['uid'], is_anon)
        result['author'] = simple_user['nickname']
        result['avatar'] = simple_user['avatar']

        if record['target']:
            result['target'] = {
                'coid': record['target']['coid'],
                'uid': record['target']['uid'],
                'content': self.xhtml_escape(record['target']['content']),
                'is_lz': record['target']['islz'],
            }

            is_target_anon = parent_coll.find_one(
                {'_id': parent_coll.to_objectid(parent_id)})['isanon'] if result['target']['is_lz'] else False

            to_user = self._user.get_simple_user(
                record['target']['uid'], is_target_anon)
            result['target']['author'] = to_user['nickname']

        return result

    def get_comments(
            self, parent, parent_id, uid=None, skip=0, limit=5, sort=[('ctime', 1)]):
        coll = self._coll_map[parent]
        parent_id = coll.to_objectid(parent_id)
        spec = {self._field_map[parent]: parent_id}
        records = coll.get_all(spec, skip=skip, limit=limit, sort=sort)

        return [self.format(rd, uid) for rd in records]

    def add_comment(
            self, parent, parent_id, uid, content, tocoid=None, is_lz=False):
        parent_id, uid, tocoid = self.to_objectids(parent_id, uid, tocoid)
        key, coll = self._field_map[parent], self._coll_map[parent]
        doc = {
            key: parent_id,
            'uid': uid,
            'target': {},
            'content': content,
            'islz': is_lz,
            'ctime': datetime.now(),
        }
        target = coll.find_one({'_id': tocoid}) if tocoid else None
        if target:
            doc['target']['coid'] = target['_id']
            doc['target']['content'] = target['content']
            doc['target']['uid'] = target['uid']
            doc['target']['islz'] = target['islz']

        coid = coll.create(doc)
        doc['_id'] = coid
        return self.format(coll.to_one_str(doc), uid)

    def like_comment(self, parent, coid, uid):
        coid, uid = self.to_objectids(coid, uid)
        self._coll_map[parent].update(
            {'_id': coid}, {'$inc': {'lnum': 1}, '$push': {'like': uid}}, w=1)


class PublicEdit(BaseHelper):

    _field_map = {
        'topics': 'tid',
        'proposals': 'pid',
    }

    _coll_map = {
        'topics': topic_model.TopicEditLog(),
        'proposals': topic_model.ProposalEditLog(),
    }

    def add_log(self, route, route_id, uid, doc):
        route_id, uid = self.to_objectids(route_id, uid)
        doc.update({'uid': uid, self._field_map[route]: route_id})
        self._coll_map[route].create(doc)
