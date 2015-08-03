#-*- coding:utf-8 -*-

#from tornado.web import authenticated
from urllib import quote

import log
import tornado.web

#from datetime import datetime
from tornado import gen

from base import BaseHandler
from base import WeiXinMixin

#from helpers import user
from config.global_setting import WEIXIN, APP_HOST

logger = log.getLogger(__file__)


class WeiXinAuthorizeHandler(BaseHandler, WeiXinMixin):

    _get_params = {
        'need': [
        ],
        'option': [
            ('next', basestring, None),
            ('code', basestring, None),
        ]
    }

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        redirect_uri = APP_HOST + self.request.uri

        if self._params['code']:
            res = yield self.get_access_token(code=self._params['code'])
            print res
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                scope=self._SCOPE['scope_base']
            )
