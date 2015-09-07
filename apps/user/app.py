#-*- coding:utf-8 -*-

import thread
from urllib import quote
from urllib import urlencode

import log
import tornado.web

#from datetime import datetime
from tornado import gen
from tornado.web import authenticated
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


class UploadTokenHandler(BaseHandler):

    @authenticated
    def get(self):
        q = Auth(QINIU['access_key'], QINIU['secret_key'])

        token = q.upload_token(
            bucket=QINIU['bucket_name']['image'],
            expires=QINIU['expires'],
            policy=QINIU['policy'],
        )

        self.wo_json({'token': token})


class PageHandler(BaseHandler, WeiXinMixin):

    _get_params = {
        'need': [
        ],
        'option': [
            ('tid', basestring, None),
            ('pid', basestring, None),
        ]
    }

    _PAGES = {
        'new': 'topic_new',
        'topic': 'topic_detail',
        'proposal': 'proposal_detail',
        'comment_list': 'comment_list',
        'personal': 'personal',
        'news_list': 'news_list',

        'following': 'personal_list',
        'publishing': 'personal_list',
    }

    _DIRECT_AUTHORIZE_PAGES = [
        'new',
        'personal',
        'news_list',
        'following',
        'publishing',
    ]

    # TODO code ugly
    def get(self, route):
        if not self.session['openid']:
            self.redirect('%s?%s' % (
                self._AUTH_BASE_URL,
                urlencode(dict(next=self.request.uri)),
            ))
            return

        authorize_url = self.get_authorize_redirect(
            redirect_uri='%s%s?%s' % (
                APP_HOST,
                self._AUTH_USERINFO_URL,
                urlencode(dict(next=self.request.uri)),
            ),
            scope=self._SCOPE['scope_userinfo']
        )

        if not self.current_user and route in self._DIRECT_AUTHORIZE_PAGES:
            self.redirect(authorize_url)
            return

        state = self._params
        state['is_authorized'] = 1 if self.current_user else 0
        state['authorize_url'] = authorize_url

        if route in ['following', 'publishing']:
            state['type'] = route

        self.render('%s.html'%self._PAGES[route], state=state)


class BaseAuthorizeHandler(BaseHandler, WeiXinMixin):

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
    def get(self):
        if not self._params['code']:
            authorize_url = self.get_authorize_redirect(
                redirect_uri=APP_HOST + self.request.uri,
                scope=self._SCOPE['scope_base']
            )
            self.render('spinner.html', authorize_url=authorize_url)
            return

        res = yield self.get_access_token(code=self._params['code'])
        if 'errcode' in res:
            raise ResponseError(5, res['errmsg'])

        user = db_user['user'].get_one({'open.wx.openid': res['openid']}) or {}
        user['openid'] = res['openid']

        self.update_session(user)
        self.redirect(self._params['next'])


class UserinfoAuthorizeHandler(BaseHandler, WeiXinMixin):

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
    def get(self):
        if not self._params['code']:
            self.authorize_redirect(
                redirect_uri=APP_HOST+self._AUTH_USERINFO_URL,
                scope=self._SCOPE['scope_userinfo']
            )
            return

        res = yield self.get_access_token(code=self._params['code'])
        if 'errcode' in res:
            raise ResponseError(5, res['errmsg'])

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
