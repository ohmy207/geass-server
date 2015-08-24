#-*- coding:utf-8 -*-

from datetime import datetime
import cPickle as pickle

import redis

from tornado.escape import xhtml_escape
#from pymongo import DESCENDING, ASCENDING

from models.user import model as user_model
from setting import COLLECTION_PREFIX as _PREFIX
from utils import escape as _es


class Helper(dict):

    __prefix = _PREFIX

    def __setitem__(self, k, v):
        return super(Helper, self).setdefault('%s%s'%(self.__prefix, self.__convert_name(k)), v)

    def __getattr__(self, name):
        collect = self.get(name, None)
        if collect is None:
            raise Exception("%s model is not found" % name)

        return collect

    def __convert_name(self, name):
        as_list = []
        length = len(name)
        for index, i in enumerate(name):
            if index !=0 and index != length-1 and i.isupper():
                as_list.append('_%s'%i.lower())
            else:
                as_list.append(i.lower())

        return ''.join(as_list)


class DataProvider(object):

    _user = user_model.User()

    def to_objectids(self, *objids):
        return map(_es.to_objectid, objids)

    def xhtml_escape(self, value):
        return xhtml_escape(value)

    def _format_time(self, time):
        time = datetime.fromtimestamp(int(time))
        total_seconds = (datetime.now() - time).total_seconds()
        #ftime = time.strftime('%Y-%m-%d %H:%M:%S')
        ftime = time.strftime('%Y-%m-%d')

        return ftime if total_seconds > 2*24*60*60 else str(total_seconds/24/60/60)+'天前' if total_seconds > 24*60*60 else str(total_seconds/60/60)+'小时前' if total_seconds > 60*60 else str(total_seconds/60)+'分钟前' if total_seconds > 60 else '刚刚'

    def get_simple_user(self, uid):
        user = self._user.get_one({'_id': self._user.to_objectid(uid)})
        return {'nickname': user['nickname'], 'avatar': user['avatar']} if user else {'nickname': '', 'avatar': ''}


#class DataProvider(object):
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
#class UserHelper(model.User):
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
#        #logging.info("user: load user %s from DB..." % uid)
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
