#-*- coding:utf-8 -*-

import log

from wechat_sdk import WechatBasic
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, EventMessage
)

from helpers.setting import WEIXIN_CONFIG

logger = log.getLogger(__file__)

MODEL_SLOTS = ['WeiXin']


class WeiXin(WechatBasic):

    def __init__(self):
        super(WeiXin, self).__init__(
            token=WX_CONFIG['token'],
            appid=WX_CONFIG['appid'],
            appsecret=WX_CONFIG['appsecret']
        )

