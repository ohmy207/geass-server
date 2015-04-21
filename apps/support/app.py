#-*- coding:utf-8 -*-

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
