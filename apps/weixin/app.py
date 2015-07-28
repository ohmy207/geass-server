#-*- coding:utf-8 -*-

import log

from wechat_sdk import WechatBasic
#from tornado.web import authenticated

from apps.base import BaseHandler

logger = log.getLogger(__file__)

wechat = WechatBasic(token='geass')


class WeiXinHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('signature', basestring, None),
            ('timestamp', basestring, None),
            ('nonce', basestring, None),
            ('echostr', basestring, None),
        ]
    }

    #@authenticated
    def get(self):
        if wechat.check_signature(signature=self._params['signature'], timestamp=self._params['timestamp'], nonce=self._params['nonce']):
            self.write(self._params['echostr'])
        else:
            self.write('fail!!!')

    def post(self):
        body_text = self.request.body
        wechat.parse_data(body_text)
        message = wechat.get_message()

        response = None
        if isinstance(message, TextMessage):
            response = wechat.response_text(content=u'������Ϣ')
        elif isinstance(message, VoiceMessage):
            response = wechat.response_text(content=u'������Ϣ')
        elif isinstance(message, ImageMessage):
            response = wechat.response_text(content=u'ͼƬ��Ϣ')
        elif isinstance(message, VideoMessage):
            response = wechat.response_text(content=u'��Ƶ��Ϣ')
        elif isinstance(message, LinkMessage):
            response = wechat.response_text(content=u'������Ϣ')
        elif isinstance(message, LocationMessage):
            response = wechat.response_text(content=u'����λ����Ϣ')
        elif isinstance(message, EventMessage):  # �¼���Ϣ
            if message.type == 'subscribe':  # ��ע�¼�(������ͨ��ע�¼���ɨ���ά����ɵĹ�ע�¼�)
                if message.key and message.ticket:  # ��� key �� ticket ����Ϊ�գ�����ɨ���ά����ɵĹ�ע�¼�
                    response = wechat.response_text(content=u'�û���δ��עʱ�Ķ�ά��ɨ���ע�¼�')
                else:
                    response = wechat.response_text(content=u'��ͨ��ע�¼�')
            elif message.type == 'unsubscribe':
                response = wechat.response_text(content=u'ȡ����ע�¼�')
            elif message.type == 'scan':
                response = wechat.response_text(content=u'�û��ѹ�עʱ�Ķ�ά��ɨ���¼�')
            elif message.type == 'location':
                response = wechat.response_text(content=u'�ϱ�����λ���¼�')
            elif message.type == 'click':
                response = wechat.response_text(content=u'�Զ���˵�����¼�')
            elif message.type == 'view':
                response = wechat.response_text(content=u'�Զ���˵���ת�����¼�')
            elif message.type == 'templatesendjobfinish':
                response = wechat.response_text(content=u'ģ����Ϣ�¼�')

        self.write(response)
