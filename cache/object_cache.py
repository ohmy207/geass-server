#-*- conding:utf-8-*-

import time
import inspect
import logging


class DataObject(object):
    '''
    object cahced by app
    '''
    __slots__ = ['name', 'expire', 'value', 'last_visit_atime', 'data_source', 'kwargs']

    def __init__(self, name, data_source, expire, **kwargs):
        self.name = name
        self.expire = expire
        self.data_source = data_source
        self.last_visit_atime = time.time()
        self.value = None
        self.kwargs = kwargs

    def is_expired(self):
        return time.time() - self.last_visit_atime > self.expire

    def update_visit_time(self):
        self.last_visit_atime = time.time()


class ObjectCache(object):
    '''
    manage cache object
    '''
    __data = {}

    @staticmethod
    def create(data_source, name=None, expire=600, **kwargs):
        if not inspect.isroutine(data_source):
            raise Exception("data_source %s must be callable function" % data_source)
        
        if not isinstance(expire, int):
            raise Exception("expire %s must be int type" % expire)

        if not name:
            raise Exception('invalid name "%s".' % name)

        if name in ObjectCache.__data:
            raise Exception('name "%s" already exists.' % name)

        obj_data = DataObject(name, data_source, expire, **kwargs)
        ObjectCache.__data[name] = obj_data

        return name

    @staticmethod
    def get(name):
        if name not in ObjectCache.__data:
            raise Exception("%s is invalid key" % name)

        obj_data = ObjectCache.__data[name]

        if obj_data.value is None or obj_data.is_expired():
            logging.info("load %s from db." % obj_data.name)
            obj_data.value = obj_data.data_source(**obj_data.kwargs)
            obj_data.update_visit_time()

        return obj_data.value

    @staticmethod
    def exists(name):
        return name and name in ObjectCache.__data

    @staticmethod
    def remove(name):
        ObjectCache.__data.pop(name, None)


def cache_get_or_create(name, load_func, expire=600):
    cache_name = name + '_cache'
    if not ObjectCache.exists(cache_name):
        ObjectCache.create(load_func, name=cache_name, expire=expire)
    return ObjectCache.get(cache_name)


if __name__ == '__main__':
    def source(a):
        return a

    ObjectCache.create(source, name='test', a=5)
    print ObjectCache.get('test')

    ObjectCache.create(source, name='test1', a=3)
    print ObjectCache.get('test1')
