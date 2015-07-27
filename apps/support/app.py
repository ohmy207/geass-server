#-*- coding:utf-8 -*-

import hashlib

#from tornado.web import authenticated
from qiniu import Auth

from apps.base import BaseHandler
from apps.setting import QINIU_CONFIG


class PageHandler(BaseHandler):

    #@authenticated
    def get(self, uid, route):
        route = route.encode('ascii')

        if route not in ['new']:
            route = 'detail'

        self.render('%s.html'%route, uid=uid)


class UploadTokenHandler(BaseHandler):

    #@authenticated
    def get(self):
        q = Auth(QINIU_CONFIG['access_key'], QINIU_CONFIG['secret_key'])

        token = q.upload_token(
            bucket=QINIU_CONFIG['bucket_name'],
            expires=QINIU_CONFIG['expires'],
            policy=QINIU_CONFIG['policy'],
        )

        self.wo_json({'token': token})


class CheckSignatureHandler(BaseHandler):

    _get_params = {
        'need': [
            ('signature', basestring),
            ('timestamp', basestring),
            ('nonce', basestring),
            ('echostr', basestring),
        ],
        'option': [
        ]
    }

    #@authenticated
    def get(self):
        token = 'geass'
        tmp_list = [token, self._params['timestamp'], self._params['nonce']]
        tmp_list.sort()
        hashcode = hashlib.sha1("%s%s%s" % tuple(tmp_list)).hexdigest()

        if hashcode == self._params['signature']:
            self.wo_json(self._params['echostr'])
        else:
            print 'wrong !!!!!!!!!!!'
