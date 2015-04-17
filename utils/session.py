"""
1. define class Session, define the interface to access session data.
   need send session_store and request params.
   session_store should support the set_session() and get_session() method.
   using request object to store the sessionid in to secure cookie.
2. define the RedisSessionStore to store session data into redis server.
   this class provider 3 api:
   get_session(sid)
   set_session(sid, session_data, expire)
   delete_session(sid)

"""
import redis
import cPickle as pickle
from uuid import uuid4
import time
from binascii import crc32

class Session(object):

    def __init__(self, session_store, session_transmission, key_prefix='picasso'):
        self._store = session_store
        self.key_prefix = key_prefix

        self._sessionid = session_transmission.get_session_id()
        if not self._sessionid:
            self._sessionid = self._generate_sid()
        session_transmission.set_session_id(self._sessionid)

        self._sessiondata = self._store.get_session(self._sessionid)
        self.dirty = False

    @property
    def sessionid(self):
        return self._sessionid

    def __getitem__(self, key):
        return self._sessiondata.get(key, None)

    def __setitem__(self, key, value):
        self._sessiondata[key] = value
        self._dirty()

    def __delitem__(self, key):
        del self._sessiondata[key]
        self._dirty()

    def __len__(self):
        return len(self._sessiondata)

    def __contains__(self, key):
        return key in self._sessiondata

    def __iter__(self):
        for key in self._sessiondata:
            yield key

    def __repr__(self):
        return self._sessiondata.__repr__()

    def __del__(self):
        if self.dirty:
            self._save()

    def clear(self):
        self._store.delete_session(self._sessionid)

    def _generate_sid(self):
        sid = '%s:%s' % (self.key_prefix, uuid4().get_hex())
        if self._store.session_id_exists(sid):
            sid = self._generate_sid()
        return sid

    def _dirty(self):
        self.dirty = True

    def _save(self):
        self._store.set_session(self._sessionid, self._sessiondata)
        self.dirty = False


class CookieSessionIdTransmission(object):

    def __init__(self, handler, cookie_name='__sid', domain='.adesk.com'):
        self.handler = handler
        self.cookie_name = cookie_name
        self.domain = domain

    def get_session_id(self):

        return self.handler.get_secure_cookie(self.cookie_name)

    def set_session_id(self, sid):

        self.handler.set_secure_cookie(self.cookie_name, sid, domain=self.domain)


class UrlSessionIdTransmission(object):

    def __init__(self, handler, key='__sid'):
        self.handler = handler
        self.key = key

    def get_session_id(self):
        return self.handler.get_argument(self.key, None)

    # do nothing, need to add this value into url yourself.
    def set_session_id(self, sid):
        pass


class HeaderSessionIdTransmission(object):

    def __init__(self, handler, header_name='X-Transmission-Session-Id'):
        self.handler = handler
        self.header_name = header_name

    def get_session_id(self):
        return self.handler.request.headers.get(self.header_name)

    def set_session_id(self, sid):
        self.handler.set_header(self.header_name, sid)


class RedisSessionStore(object):

    def __init__(self, redis_hosts, **options):
        self.redis_pool = [redis.Redis(host=h, port=p, db=db) for h, p, db in redis_hosts]

    def __get_redis_connection(self, sid):
        idx = crc32(sid) % len(self.redis_pool)
        return self.redis_pool[idx]

    def get_session(self, sid):
        # TODO get
        data = self.__get_redis_connection(sid).hget(sid, 'data')

        return pickle.loads(data) if data else dict()

    def set_session(self, sid, session_data, expire=43200):
        self.__get_redis_connection(sid).hset(
            sid, 'data', pickle.dumps(session_data))
        self.__get_redis_connection(sid).expire(sid, expire)

    def delete_session(self, sid):
        self.__get_redis_connection(sid).delete(sid)

    def session_id_exists(self, sid):
        return sid and self.__get_redis_connection(sid).exists(sid)


if __name__ == '__main__':
    import tornado.ioloop
    import tornado.web
    import redis

    class MainHandler(tornado.web.RequestHandler):

        def get(self, name):

            oname = self.get_current_user() or 'world'
            self.write("Hello, %s, the old name is %s." % (name, oname))
            if oname != name:
                self.session['user'] = name
                self.write("<br />Name not equal set new name %s." % name)

        def get_current_user(self):

            return self.session['user'] if self.session and 'user' in self.session else None

        @property
        def session(self):

            return Session(self.application.settings['session_store'], CookieSessionIdTransmission(self))

    # TODO session_store
    application = tornado.web.Application([(r"/(\w+)", MainHandler)], session_store=RedisSessionStore(
        [('127.0.0.1', 6379, 0)]), cookie_secret='aVD321fQAGaYdkLlsd334K#/adf22iNvdfdflle3fl$=')

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
