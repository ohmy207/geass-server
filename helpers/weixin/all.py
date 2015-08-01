#-*- coding:utf-8 -*-

import log

from wechat_sdk import WechatBasic
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage
)

from config.global_setting import WX

logger = log.getLogger(__file__)

MODEL_SLOTS = ['WeiXin']


class WeiXin(WechatBasic):

    def __init__(self):
        super(WeiXin, self).__init__(
            token=WX['token'],
            appid=WX['appid'],
            appsecret=WX['appsecret']
        )
