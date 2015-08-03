#-*- coding:utf-8 -*-

#from tornado.web import authenticated
from urllib import quote

import log
import tornado.web

#from datetime import datetime
from tornado import gen

from .base import BaseHandler
from .base import WeiXinMixin
from apps.base import ResponseError

from helpers import user as db_user
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
        code = self._params['code']
        redirect_uri = APP_HOST + self.request.uri

        if code:
            res = yield self.get_access_token(code=code)

            if 'errcode' in res:
                raise ResponseError(5)

            access_token,openid,scope = res['access_token'],res['openid'],res['scope']

            if scope == self._SCOPE['scope_base']:
                user =  db_user['user'].get_one({'open.wx.openid': openid})
                if not user:
                    return self.authorize_redirect(
                        redirect_uri=redirect_uri,
                        scope=self._SCOPE['scope_userinfo']
                    )

            else:
            #elif scope == self._SCOPE['scope_userinfo']:
                user = yield self.get_authenticated_user(
                        access_token=access_token,
                        openid=openid,
                    )

                if 'errcode' in user:
                    raise ResponseError(5, user['errmsg'])

                uid = db_user['user'].create({'open': {'wx': user}})
                user = db_user['user'].get_one({'_id': uid})

            self.update_session(user)
            self.redirect(self._params['next'] or '/')
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                scope=self._SCOPE['scope_base']
            )
