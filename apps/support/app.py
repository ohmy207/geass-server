#-*- coding:utf-8 -*-

from tornado.web import authenticated
from qiniu import Auth

from apps.base import BaseHandler
from config.global_setting import QINIU


class PageHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('tid', basestring, None),
            ('pid', basestring, None),
        ]
    }

    @authenticated
    def get(self, route):

        pages = {
            'new': 'topic_new',
            'topic': 'topic_detail',
            'proposal': 'proposal_detail',
            'comments': 'comment_list',
        }

        self.render('%s.html'%pages[route], state=self._params)


class UploadTokenHandler(BaseHandler):

    @authenticated
    def get(self):
        q = Auth(QINIU['access_key'], QINIU['secret_key'])

        token = q.upload_token(
            bucket=QINIU['bucket_name'],
            expires=QINIU['expires'],
            policy=QINIU['policy'],
        )

        self.wo_json({'token': token})
