# -*- coding:utf-8 -*-

from tornado.web import authenticated

import log
from helpers import topic as db_topic
from helpers import user as db_user

from .base import BaseHandler

logger = log.getLogger(__file__)


class HomeHandler(BaseHandler):

    @authenticated
    def get(self):
        self.render('index.html', puppets='')


class LoginHandler(BaseHandler):

    _post_params = {
        'need': [
            ('username', basestring),
            ('password', basestring),
        ],
        'option': [
            ('next', basestring, '/'),
        ]
    }

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 15),
        ]
    }

    special_users = ['569e088e3e9ff6721a8f8e81', '569dd28c3e9ff6720f61b0b1',
                     '569cb0213e9ff6720f61b0aa', '569caab33e9ff6720f61b0a2',
                     '56a0d08b3e9ff62784eaa034', '56a0d0363e9ff62784eaa033']

    def post(self):
        username = self._params['username']
        password = self._params['password']

        if not username or not password:
            return self.render('login.html', msg='用户名或密码不能为空')

        user = db_user['user'].find_one({'open.wx.nickname': username})
        if not user or password != 't66y' or unicode(user['_id']) not in self.special_users:
            return self.render('login.html', msg='用户名或密码有误')

        self.update_session({'uid': unicode(user['_id']), 'openid': user['open']['wx']['openid']})
        self.redirect(self._params['next'])

    def get(self):
        self.render('login.html', msg='')
