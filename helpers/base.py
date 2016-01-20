# -*- coding:utf-8 -*-

# import cPickle as pickle
from datetime import datetime

# import redis
from tornado.escape import xhtml_escape

from config.global_setting import ANONYMOUS_USER, DEFAULT_USER, PIC_URL
from models.user import model as user_model
from utils import escape as _es

from .setting import COLLECTION_PREFIX as _PREFIX


# from pymongo import DESCENDING, ASCENDING


class Helper(dict):

    __prefix = _PREFIX

    def __setitem__(self, k, v):
        return super(Helper, self).setdefault(
            '%s%s' % (self.__prefix, self.__convert_name(k)), v)

    def __getattr__(self, name):
        collect = self.get(name, None)
        if collect is None:
            raise Exception("%s model is not found" % name)

        return collect

    def __convert_name(self, name):
        as_list = []
        length = len(name)
        for index, i in enumerate(name):
            if index != 0 and index != length - 1 and i.isupper():
                as_list.append('_%s' % i.lower())
            else:
                as_list.append(i.lower())

        return ''.join(as_list)


class BaseHelper(object):

    @staticmethod
    def to_objectids(*objids):
        return map(_es.to_objectid, objids)

    @staticmethod
    def xhtml_escape(value):
        return xhtml_escape(value)

    @staticmethod
    def _format_time(time):
        time = datetime.fromtimestamp(int(time))
        total_seconds = int((datetime.now() - time).total_seconds())
        #ftime = time.strftime('%Y-%m-%d %H:%M:%S')
        return time.strftime('%Y-%m-%d')

    # TODO
    @staticmethod
    def _simple_time(time):
        time = datetime.fromtimestamp(int(time))
        total_seconds = int((datetime.now() - time).total_seconds())
        #ftime = time.strftime('%Y-%m-%d %H:%M:%S')
        ftime = time.strftime('%Y-%m-%d')

        return ftime if total_seconds > 2 * 24 * 60 * 60 else str(total_seconds / 24 / 60 / 60) + '天前' if total_seconds > 24 * 60 * 60 else str(
            total_seconds / 60 / 60) + '小时前' if total_seconds > 60 * 60 else str(total_seconds / 60) + '分钟前' if total_seconds > 60 else '刚刚'


class UserHelper(BaseHelper, user_model.User):

    @staticmethod
    def callback(record):
        result = {
            'uid': record['_id'],
            'nickname': record['nickname'] or record['open']['wx']['nickname'],
            'avatar': PIC_URL['avatar'](record['avatar']) if record['avatar'] else record['open']['wx']['headimgurl'] if record['open']['wx']['headimgurl'] else DEFAULT_USER['avatar'],
            'sex': record['sex'] or record['open']['wx']['sex'],
        }

        return result

    def get_simple_user(self, uid, isanon=False):
        user = ANONYMOUS_USER if isanon else self.get_one(
            {'_id': self.to_objectid(uid)})
        return {'nickname': user['nickname'], 'avatar': user['avatar']} if user else {
            'nickname': '', 'avatar': ''}


# class DataProvider(object):
#
#    def get_all(self, spec=None, skip=0, limit=20, order=None, sort=None):
#
#        if order:
#            sort = order == 'new' and [('atime', DESCENDING)] or (order == 'hot' and [('rank', DESCENDING)]) or sort
#
#        return self.to_str(self.find(spec=spec, skip=skip, limit=limit, sort=sort), self.callback or None)
#
#    def get_one(self, objid):
#
#        if isinstance(objid, str):
#            objid = to_objectid(objid)
#        rd = self.find_one(objid) or None
#        if rd:
#            if hasattr(self, 'callback'):
#                return self.callback(self.to_one_str(rd))
#
#            return self.to_one_str(rd)
#        return None
#
#    def get_related_album(self, module):
#        pass
#
#    def get_count(self, spec=None):
#        return self.find(spec=spec).count()
#
#
# class UserHelper(model.User):
#
#    def __init__(self, host='127.0.0.1', port=6379, db=1, master=True):
#        super(UserHelper, self).__init__()
#        self.port = port
#        self.host = host
#        self.db = db
#
#        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)
#
#    def get_simple_user(self, uid, duration=600):
#        key = str(uid)
#        if self.r.exists(key):
#            try:
#                return pickle.loads(self.r.get(key))
#            except:
#                pass
#        logging.info("user: load user %s from DB..." % uid)
#        user = self.load_simple_user(uid)
#        self.r.set(key, pickle.dumps(user))
#        self.r.expire(key, duration)
#        return user
#
#    def load_simple_user(self, uid):
#
#        def get_attr(rd, attr, default = None):
#            return rd and isinstance(rd, dict) and rd.get(attr) or default
#
#        u = self.find_by_id(uid)
#        if u:
#            name = get_attr(u, 'nickname', get_attr(u['open'].get('weixin'), 'nickname', get_attr(u['open'].get('sina'), 'nickname', get_attr(u['open'].get('qq'), 'nickname', None))))
#            aid = get_attr(u['avatar'], 'avatar', get_attr(u['avatar'], 'thumb'))
#            if aid:
#                avatar = DOWNLOAD_URL['img'](aid)
#            else:
#                avatar = get_attr(u['open'].get('weixin'), 'avatar', get_attr(u['open'].get('sina'), 'avatar', get_attr(u['open'].get('qq'), 'avatar', 'http://s.androidesk.com/picasso/avatar_default.png')))
#
#            return {'id': str(u['_id']), 'name': name, 'avatar': avatar}
#
#        return {'id': '4d5a2259716ec209a4000000', 'name': '安卓壁纸蛋蛋君', 'avatar': 'http://s.androidesk.com/picasso/avatar_default.png'}
#
