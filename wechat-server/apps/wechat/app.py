#-*- coding:utf-8 -*-

import log

#from tornado.web import authenticated

from apps.base import BaseHandler

from helpers import wechat as wc

logger = log.getLogger(__file__)


class WeiXinHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('echostr', basestring, None),
            ('nonce', basestring, None),
            ('signature', basestring, None),
            ('timestamp', basestring, None),
        ]
    }

    # server verify
    def get(self):
       if wc['wechat'].check_signature(signature=self._params['signature'], timestamp=self._params['timestamp'], nonce=self._params['nonce']):
           self.write(self._params['echostr'])

    def post(self):
        # if wc['wechat'].check_signature(signature=self._params['signature'], timestamp=self._params['timestamp'], nonce=self._params['nonce']):
        #   body_text = self.request.body
        pass
