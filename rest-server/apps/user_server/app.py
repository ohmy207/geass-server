#-*- coding:utf-8 -*-

import thread
from urllib import quote
from urllib import urlencode
#from datetime import datetime

import log
import tornado.web

from tornado import gen
from tornado.web import authenticated
from qiniu import Auth, BucketManager

from .base import BaseHandler
from .base import WeiXinMixin
from apps.base import ResponseError

from helpers import user as db_user
from helpers import wechat as wc
from cache.object_cache import ObjectCache
from config.global_setting import WEIXIN, APP_HOST, QINIU

logger = log.getLogger(__file__)


class PuppetsHandler(BaseHandler):

    _post_params = {
        'need': [
            ('uid', basestring),
        ],
        'option': [
        ]
    }

    special_users = ['569e088e3e9ff6721a8f8e81', '569dd28c3e9ff6720f61b0b1',
        '569cb0213e9ff6720f61b0aa', '569caab33e9ff6720f61b0a2']

    def get(self):
        uid = self.to_objectid(self.session['origin_uid']) or self.current_user

        if unicode(uid) not in self.special_users:
            self.redirect('/')
            return

        puppets = db_user['user'].get_all({'open': {}})
        current_user = db_user['user'].get_one({'_id': uid})
        puppets.insert(0, current_user)

        self.render('puppet_list.html', puppets=puppets)

    def post(self):
        uid = self.to_objectid(self.session['origin_uid']) or self.current_user

        if unicode(uid) in self.special_users:
            if not self.session['origin_uid']:
                self.session['origin_uid'] = unicode(uid)
            self.session['uid'] = self._params['uid']

        self.redirect('/')


class ForbiddenHandler(BaseHandler):

    def GET(self):
        raise ResponseError(403)


class UploadTokenHandler(BaseHandler):

    def load_upload_token(self):
        q = Auth(QINIU['access_key'], QINIU['secret_key'])
        return q.upload_token(
            bucket=QINIU['bucket_name']['image'], expires=QINIU['expires'], policy=QINIU['policy'])

    @authenticated
    def get(self):
        name = 'upload_token'
        if not ObjectCache.exists(name):
            ObjectCache.create(self.load_upload_token, name=name, expire=3600)
        self.wo_json({'token': ObjectCache.get(name)})


class PageHandler(BaseHandler, WeiXinMixin):

    _get_params = {
        'need': [
        ],
        'option': [
            ('tid', basestring, ''),
            ('pid', basestring, ''),
            ('oid', basestring, ''),
            ('parent', basestring, ''),
            ('parent_id', basestring, ''),
            ('pos', int, 0),
        ]
    }

    _PAGES = {
        'home': 'home',
        'new': 'topic_new',
        'topic': 'topic_detail',
        'proposal': 'proposal_detail',
        'opinion': 'opinion_detail',
        'comment_list': 'comment_list',
        'personal': 'personal',
        'notice_list': 'notice_list',

        'following': 'personal_list',
        'publish_topics': 'personal_list',
        'publish_opinions': 'personal_list',

        'help_list': 'help_list',
        'help': 'help',
    }

    _DIRECT_AUTHORIZE_PAGES = [
        'new',
        'personal',
        'notice_list',
        'following',
        'publish_topics',
        'publish_opinions',
    ]

    # TODO code ugly
    def get(self, route):
        if not self.session['openid']:
            self.redirect('%s?%s' % (
                self._AUTH_BASE_URL,
                urlencode(dict(next=self.request.uri)),
            ))
            return

        route = route or 'home'
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
        for k,v in state.iteritems():
            if k not in ['tid', 'pid']:
                continue
            state[k] = v if self.to_objectid(v) else ''

        state['is_authorized'] = 1 if self.current_user else 0
        state['authorize_url'] = authorize_url
        state['sign_package'] = wc['wechat'].get_jssign_package(
            APP_HOST + self.request.uri)

        if route in ['following', 'publish_topics', 'publish_opinions']:
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
            logger.error('AuthorizeError: %s, %s' % (5, res['errmsg']))
            self.http_error(401)

        user = db_user['user'].get_one({'open.wx.openid': res['openid']}) or {}
        user['openid'] = res['openid']

        self.update_session(user)
        self.redirect(self._params['next'])


class UserInfoAuthorizeHandler(BaseHandler, WeiXinMixin):

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
            logger.error('AuthorizeError: %s, %s' % (5, res['errmsg']))
            self.http_error(401)

        user = db_user['user'].get_one({'open.wx.openid': res['openid']}) or None
        if user:
            self.update_session(user)
            self.redirect(self._params['next'])
            return

        user = yield self.get_authenticated_user(
            access_token=res['access_token'],
            openid=res['openid'],
        )

        if 'errcode' in user:
            logger.error('AuthorizeError: %s, %s' % (5, user['errmsg']))
            self.http_error(401)

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

