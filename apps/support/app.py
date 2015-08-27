#-*- coding:utf-8 -*-

try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3

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

    def get(self, route):
        if not self.session['openid']:
            url = '/wx/authorize/openid'
            url += "?" + urlencode(dict(next=self.request.uri))
            self.redirect(url)
            return

        pages = {
            'new': 'topic_new',
            'topic': 'topic_detail',
            'proposal': 'proposal_detail',
            'comments': 'comment_list',
        }
        state = self._params
        state['is_registered'] = 1 if self.current_user else 0

        self.render('%s.html'%pages[route], state=state)


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
