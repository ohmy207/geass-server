#-*- coding:utf-8 -*-

import string
import random
import time

import log

from wechat_sdk import WechatBasic
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage
)

from config.global_setting import WEIXIN

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Wechat']


class Wechat(WechatBasic):

    def __init__(self):
        super(Wechat, self).__init__(
            token=WEIXIN['token'], appid=WEIXIN['appid'], appsecret=WEIXIN['appsecret'])

    def _create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def _create_timestamp(self):
        return int(time.time())

    def get_jssign_package(self, url):
        sign_package = {
            'appId': WEIXIN['appid'],
            'timestamp': self._create_timestamp(),
            'nonceStr': self._create_nonce_str()
        }
        sign_package['signature'] = self.generate_jsapi_signature(
            sign_package['timestamp'], sign_package['nonceStr'], url, jsapi_ticket=None)
        return sign_package

