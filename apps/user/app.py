#-*- coding:utf-8 -*-

import thread
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
from config.global_setting import WEIXIN, APP_HOST, QINIU

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
                raise ResponseError(5, res['errmsg'])

            access_token,openid,scope = res['access_token'],res['openid'],res['scope']

            if scope == self._SCOPE['scope_base']:
                user =  db_user['user'].get_one({'open.wx.openid': openid})
                if not user:
                    self.authorize_redirect(
                        redirect_uri=redirect_uri,
                        scope=self._SCOPE['scope_userinfo']
                    )
                    return

            else:
            #elif scope == self._SCOPE['scope_userinfo']:
                user = yield self.get_authenticated_user(
                        access_token=access_token,
                        openid=openid,
                    )

                if 'errcode' in user:
                    raise ResponseError(5, user['errmsg'])

                uid = db_user['user'].create({'open': {'wx': user}})
                user['uid'] = unicode(uid)
                #user = db_user['user'].get_one({'_id': uid})
                thread.start_new_thread(self.backup_avatar, (uid, user['headimgurl']))

            self.update_session(user)
            self.redirect(self._params['next'] or '/')
        else:
            self.authorize_redirect(
                redirect_uri=redirect_uri,
                scope=self._SCOPE['scope_base']
            )

    def backup_avatar(self, uid, avatar):
        if not avatar.startswith('http'):
            logger.error('avatar url is error, url: %s' % avatar)
            return

        ret, info = bucket.fetch(avatar, QINIU['bucket_name']['avatar'])
        if not ret or 'error' in ret:
            logger.error('upload avatar failed, info: %s avatar url: %s' % (info, avatar))
            return

        db_user['user'].update({'_id': self.to_objectid(uid)}, {'$set': {'avatar': ret['key']}}, w=1)
