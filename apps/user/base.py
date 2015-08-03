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
    #def get_authenticated_user(self, code, callback, grant_type='authorization_code'):
        args = {
            'appid': self._APP_ID,
            'secret': self._APP_SECRET,
            'code': code,
            'grant_type': grant_type,
        }

        http = self.get_auth_http_client()
        http.fetch(url_concat(self._ACCESS_TOKEN_URL, args),
                   self.async_callback(self._on_access_token, callback))

    def _on_access_token(self, callback, response):
        if response.error:
            future.set_exception(AuthError('weixin auth error %s' % str(response)))
            return

        future.set_result(escape.json_decode(response.body))

        #http = self.get_auth_http_client()
        #http.fetch(url_concat(self._USERINFO_URL, args), self.async_callback(self._on_access_openid, redirect_uri, client_id, client_secret, session, callback, fields))

    def _on_access_openid(self, redirect_uri, client_id, client_secret, session,
                          future, fields, response):
        if response.error:
            future.set_exception(AuthError('Error response % fetching %s',
                                           response.error, response.request.url))
            return
        
        res = re.search(r'"openid":"([a-zA-Z0-9]+)"', escape.native_str(response.body))

        session['openid'] = res.group(1)
        session['client_id'] = client_id

        self.qq_request(
            path='/user/get_user_info',
            callback=self.async_callback(
                self._on_get_user_info, future, session, fields),
            access_token=session['access_token'],
            openid=session['openid'],
            client_id=session['client_id'],
            )

    def _on_get_user_info(self, future, session, fields, user):
        if user is None:
            future.set_result(None)
            return

        fieldmap = {}
        for field in fields:
            fieldmap[field] = user.get(field)

        fieldmap.update({'access_token': session['access_token'], 'session_expires': session.get('expires'), 
                         'openid': session['openid']})

        future.set_result(fieldmap)

    @_auth_return_future
    def qq_request(self, path, callback, access_token=None, openid=None, client_id=None, 
                   format='json', post_args=None, **args):
        url = 'https://graph.qq.com' + path
        all_args = {}
        if access_token:
            all_args['access_token'] = access_token
        if openid:
            all_args['openid'] = openid
        if client_id:
            all_args['oauth_consumer_key'] = client_id
        if args:
            all_args.update(args)

        if all_args:
            all_args.update({'format': format})
            url += '?' + urllib_parse.urlencode(all_args)
        callback = self.async_callback(self._on_qq_request, callback)
        http = self.get_auth_http_client()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib_parse.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_qq_request(self, future, response):
        if response.error:
            future.set_exception(AuthError('Error response %s fetching %s', 
                                           response.error, response.request.url))
            return

        future.set_result(escape.json_decode(response.body))

    def get_auth_http_client(self):
        return httpclient.AsyncHTTPClient()
