#-*- coding:utf-8 -*-

import re

from tornado import gen
from tornado import httpclient
from tornado import escape
from tornado.httputil import url_concat
from tornado.concurrent import Future
from tornado.auth import OAuth2Mixin, _auth_return_future, AuthError

from apps import base
from config.global_setting import WEIXIN

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    import urllib.parse as urllib_parse
except ImportError:
    import urllib as urllib_parse


class BaseHandler(base.BaseHandler):
    pass


class WeiXinMixin(OAuth2Mixin):

    _APP_ID = WEIXIN['appid']
    _APP_SECRET = WEIXIN['appsecret']

    _SCOPE = WEIXIN['scope']
    _AUTHORIZE_URL = WEIXIN['authorize_url']
    _AUTHORIZE_URL_SUFFIX = WEIXIN['authorize_url_suffix']
    _ACCESS_TOKEN_URL = WEIXIN['access_token_url']
    _USERINFO_URL = WEIXIN['userinfo_url']

    def authorize_redirect(self, redirect_uri=None, response_type='code', scope=None, state=None):
        args = {
            'appid': self._APP_ID,
            'redirect_uri': redirect_uri,
            'response_type': response_type,
            'scope': scope,
            'state': state,
        }

        self.redirect('%s%s' % (url_concat(self._AUTHORIZE_URL, args), self._AUTHORIZE_URL_SUFFIX))

    @_auth_return_future
    def get_access_token(self, code, callback, grant_type='authorization_code'):
        args = {
            'appid': self._APP_ID,
            'secret': self._APP_SECRET,
            'code': code,
            'grant_type': grant_type,
        }

        http = self.get_auth_http_client()
        http.fetch(url_concat(self._ACCESS_TOKEN_URL, args),
                   self.async_callback(self._on_access_token, callback))

    @_auth_return_future
    def get_authenticated_user(self, code, callback, lang='zh_CN'):
        args = {
            'access_token': access_token,
            'openid': openid,
            'lang': lang,
        }

        http = self.get_auth_http_client()
        http.fetch(url_concat(self._USERINFO_URL, args),
                   self.async_callback(self._on_authenticated_user, callback))

    def _on_access_token(self, future, response):
        if response.error:
            future.set_exception(AuthError('weixin auth error %s' % str(response)))
            return

        future.set_result(escape.json_decode(response.body))

    def _on_authenticated_user(self, future, response):
        if response.error:
            future.set_exception(AuthError('Error response %s fetching %s', 
                                           response.error, response.request.url))
            return

        future.set_result(escape.json_decode(response.body))

    def get_auth_http_client(self):
        return httpclient.AsyncHTTPClient()
