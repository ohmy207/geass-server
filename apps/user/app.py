#-*- coding:utf-8 -*-

#from tornado.web import authenticated

import log
import tornado.web

#from datetime import datetime
from tornado import gen

from base import BaseHandler
from base import OAuth2Mixin

#from helpers import user
from config.global_setting import WX, WX_URL

logger = log.getLogger(__file__)


class WeiXinAuthorizeHandler(BaseHandler, OAuth2Mixin):

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
        print self._params
        print self.request.uri

        if self._params['code']:
            user = yield self.get_authenticated_user(
                access_token_url=WX_URL['access_token_url'](self._params['code'])
            )
            #self.render('qq.html', user=user)
        else:
            self.authorize_redirect(
                authorize_url=WX_URL['authorize_url'](
                    redirect_uri=self.request.uri,
                    scope=WX['scope_base'],
                    state=None,
                )
            )
