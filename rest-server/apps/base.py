# -*- coding:utf-8 -*-

import tornado.web
from bson import json_util
from bson.objectid import ObjectId

import log
from config.global_setting import CDN, ERROR_PAGE_MESSAGE, MESSAGE
from utils import escape as _es
from utils import httputil as _ht
from utils import session

logger = log.getLogger(__file__)


class ResponseError(Exception):

    def __init__(self, code=None, msg=None):
        self.code = code
        self.msg = msg
        super(ResponseError, self).__init__(msg)

    def __str__(self):
        return '%s %s' % (self.code, self.msg)


class BaseHandler(tornado.web.RequestHandler):

    '''
    config request parameter like this:
    _get_params = {
            'need':[
                ('skip', int),
                ('limit', int),
            ],
            'option':[
                ('jsoncallback', basestring, None),
            ]
        }

    '''

    #_required_params = [('jsoncallback', basestring, None), ('skip', int, 0), ('limit', int, 0)]
    _types = [ObjectId, None, basestring, int, float, list, bool]
    _data = None
    _jump = None

    _session = None

    def initialize(self):
        super(BaseHandler, self).initialize()
        self._skip = 0
        self._limit = 0

    def prepare(self):
        super(BaseHandler, self).prepare()
        self._skip = abs(self._params['skip']) if self._params.get('skip', None) else 0
        self._limit = abs(self._params['limit']) if self._params.get('limit', None) else 5

    def to_objectid(self, objid):
        return _es.to_objectid(objid)

    def to_int(self, value):
        return _es.to_int(value)

    def to_float(self, value):
        return _es.to_float(value)

    def to_bool(self, value):
        return _es.to_bool(value)

    def utf8(self, v):
        return tornado.escape.utf8(v)

    def json_encode(self, data):
        return _es.json_encode(data)

    def json_decode(self, data):
        return _es.json_decode(data)

    # write output json
    def wo_json(self, data):
        self.write(self.json_encode(data))

    def get_son(self, name):
        try:
            json_str = self.get_argument(name, '{}')
            obj = json.loads(json_str, object_hook=json_util.object_hook)
        except (ValueError, TypeError):
            logger.error('couldn\'t parse json: %s' % json_str)
            return None

        if getattr(obj, '__iter__', False) == False:
            logger.error('type is not iterable: %s' % json_str)
            return None
        return obj

    def get(self, *args, **kwargs):
        try:
            self.GET(*args, **kwargs)
        except ResponseError as e:
            e.msg = MESSAGE.get(e.code)
            logger.error('ResponseError: %s, %s' % (e.code, e.msg))
            resp = self.init_resp(e.code)
        except Exception as e:
            logger.exception(e)
            resp = self.init_resp(1)
        else:
            resp = self.init_resp()

        self.wo_resp(resp)

    def post(self, *args, **kwargs):
        try:
            self.POST(*args, **kwargs)
        except ResponseError as e:
            e.msg = MESSAGE.get(e.code)
            logger.error('ResponseError: %s, %s' % (e.code, e.msg))
            resp = self.init_resp(e.code)
        except Exception as e:
            logger.exception(e)
            resp = self.init_resp(1)
        else:
            resp = self.init_resp()

        self.wo_resp(resp)

    def delete(self, *args, **kwargs):
        try:
            self.DELETE(*args, **kwargs)
        except ResponseError as e:
            e.msg = MESSAGE.get(e.code)
            logger.error('ResponseError: %s, %s' % (e.code, e.msg))
            resp = self.init_resp(e.code)
        except Exception as e:
            logger.exception(e)
            resp = self.init_resp(1)
        else:
            resp = self.init_resp()

        self.wo_resp(resp)

    def patch(self, *args, **kwargs):
        try:
            self.PATCH(*args, **kwargs)
        except ResponseError as e:
            e.msg = MESSAGE.get(e.code)
            logger.error('ResponseError: %s, %s' % (e.code, e.msg))
            resp = self.init_resp(e.code)
        except Exception as e:
            logger.exception(e)
            resp = self.init_resp(1)
        else:
            resp = self.init_resp()

        self.wo_resp(resp)

    @staticmethod
    def init_resp(code=0, msg=None):
        resp = {
            'code': code,
            'msg': MESSAGE.get(code),
        }

        return resp

    def GET(self, *args, **kwargs):
        pass

    def POST(self, *args, **kwargs):
        pass

    def DELETE(self, *args, **kwargs):
        pass

    def PATCH(self, *args, **kwargs):
        pass

    def route(self, route, *args, **kwargs):
        getattr(self,  "do_%s" % route, lambda *args, **kwargs: None)(*args, **kwargs)

    def wo_resp(self, resp):
        if resp['code'] != 0:
            return self.wo_json(resp)

        if isinstance(self._data, dict):
            #resp['data'].update(self._data)
            resp['data'] = self._data

        if isinstance(self._jump, basestring):
            resp['jumpURL'] = self._jump

        return self.wo_json(resp)

    @property
    def _params(self):
        '''
        according to request method config to filter all request paremter
        if value is invalid then set None
        '''
        method = self.request.method.lower()
        arguments = self.request.arguments

        rpd = {}  # request parameter dict

        def filter_parameter(key, tp, default=None):
            if tp not in self._types:
                raise ValueError("%s parameter expected types %s" % (key, self._types))

            if key not in arguments:
                rpd[key] = default
                return

            if tp in [ObjectId, int, float, bool]:
                rpd[key] = getattr(self, 'to_%s' % getattr(tp, '__name__').lower())(self.get_argument(key))
                return

            if tp == basestring:
                rpd[key] = self.get_argument(key, strip=False)
                return

            if tp == list:
                rpd[key] = self.get_arguments(key)
                return

        #for key, tp, default in self._required_params:
        #    filter_parameter(key, tp, default)

        params = getattr(self, '_%s_params' % method, None)
        if params is None:
            return rpd

        #need parameter
        for key, tp in params.get('need', []):
            if tp == list:
                filter_parameter(key, tp, [])
            else:
                filter_parameter(key, tp)

        #option parameter
        for key, tp, default in params.get('option', []):
            filter_parameter(key, tp, default)

        return rpd

    def write_error(self, status_code, **kwargs):
        msg = ERROR_PAGE_MESSAGE[500]

        if status_code in [401, 403, 404]:
            msg = ERROR_PAGE_MESSAGE[status_code]

        self.render("error.html", error_code=status_code, msg=msg)

    def http_error(self, status_code):
        raise tornado.web.HTTPError(status_code)

    @property
    def session(self):
        if not self._session:
            self._session = session.Session(self.application.settings['session_store'], session.CookieSessionIdTransmission(self))
        return self._session

    def update_session(self, user):
        if not user:
            return self.session.clear()

        for k,v in user.iteritems():
            if k in ['uid', 'openid']:
                self.session[k] = v
        #if user:
        #    self.session['uid'] = user['uid']
        #    self.session['openid'] = user['openid']
        #    #self.session['sex'] = user['sex']
        #    #self.session['avatar'] = user['avatar']
        #    #self.session['nickname'] = user['nickname']
        #else:
        #    self.session.clear()

    def get_current_user(self):
        return self.to_objectid(self.session['uid'])
        #return self.to_objectid(self.session['uid']) if self.session and 'uid' in self.session else None

    def static_url(self,  path, include_host=None, v=None, **kwargs):
        is_debug = self.application.settings.get('debug', False)

        # In debug mode, load static files from localhost
        if is_debug or is_debug ^ CDN['is_disabled']:
            return super(BaseHandler, self).static_url(path, include_host, **kwargs)

        v = 1

        if v:
            return '%s/%s?v=%s' % (CDN['host'], path, v)
        else:
            return '%s/%s' % (CDN['host'], path)

