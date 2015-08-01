#-*- coding:utf-8 -*-

#from tornado.web import authenticated
from qiniu import Auth

from apps.base import BaseHandler
from config.global_setting import QINIU


#class PageHandler(BaseHandler):
#
#    #@authenticated
#    def get(self, uid, route):
#        route = route.encode('ascii')
#
#        if route not in ['new']:
#            route = 'detail'
#
#        self.render('%s.html'%route, uid=uid)


class UploadTokenHandler(BaseHandler):

    #@authenticated
    def get(self):
        q = Auth(QINIU['access_key'], QINIU['secret_key'])

        token = q.upload_token(
            bucket=QINIU['bucket_name'],
            expires=QINIU['expires'],
            policy=QINIU['policy'],
        )

        self.wo_json({'token': token})
