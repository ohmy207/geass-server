#-*- coding:utf-8 -*-

import thread
#from tornado.web import authenticated
from urllib import quote

import log
import tornado.web

#from datetime import datetime
from tornado import gen
from qiniu import Auth, BucketManager

from .base import BaseHandler
from .base import WeiXinMixin
from apps.base import ResponseError

from helpers import user as db_user
from config.global_setting import WEIXIN, APP_HOST, QINIU

logger = log.getLogger(__file__)


class ForbiddenHandler(BaseHandler):

    def GET(self):
        raise ResponseError(403)


class WeiXinAuthorizeHandler(BaseHandler, WeiXinMixin):

    _get_params = {
        'need': [
        ],
        'option': [
            ('next', basestring, '/'),
            ('code', basestring, None),
        ]
    }

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, route):
        if self._params['code']:
            res = yield self.get_access_token(code=self._params['code'])
            if 'errcode' in res:
                raise ResponseError(5, res['errmsg'])

            self.route(route, res)
            return

        if route == 'openid':
            redirect_url = self.get_authorize_redirect(
                redirect_uri=APP_HOST + self.request.uri,
                scope=self._SCOPE['scope_base']
            )
            self.render('spinner.html', redirect_url=redirect_url)

        if route == 'userinfo':
            self.authorize_redirect(
                redirect_uri=APP_HOST + '/wx/authorize/userinfo',
                scope=self._SCOPE['scope_userinfo']
            )
            return

    def do_openid(self, res):
        user = db_user['user'].get_one({'open.wx.openid': res['openid']}) or {}
        user['openid'] = res['openid']
        self.update_session(user)
        self.redirect(self._params['next'])

    @tornado.web.asynchronous
    @gen.coroutine
    def do_userinfo(self, res):
        user = yield self.get_authenticated_user(
            access_token=res['access_token'],
            openid=res['openid'],
        )

        if 'errcode' in user:
            raise ResponseError(5, user['errmsg'])

        uid = db_user['user'].create({'open': {'wx': user}})
        thread.start_new_thread(self.backup_avatar, (uid, user['headimgurl']))
        # TODO format user
        user = {'uid': unicode(uid), 'openid': res['openid']}
        self.update_session(user)
        self.redirect(self._params['next'])

    def backup_avatar(self, uid, avatar):
        if not avatar.startswith('http'):
            logger.error('avatar url is error, url: %s' % avatar)
            return

        # TODO storge q
        q = Auth(QINIU['access_key'], QINIU['secret_key'])
        bucket = BucketManager(q)

        ret, info = bucket.fetch(avatar, QINIU['bucket_name']['avatar'])
        if not ret or 'error' in ret:
            logger.error('upload avatar failed, info: %s avatar url: %s' % (info, avatar))
            return

        db_user['user'].update({'_id': self.to_objectid(uid)}, {'$set': {'avatar': ret['key']}}, w=1)
