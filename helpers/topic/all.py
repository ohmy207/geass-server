#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.topic import model as topic

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic']


class Topic(topic.Topic):

    @staticmethod
    def callback(record):
        result = {
            'title': record['title'],
            'content': record['content'],
            'authoruid': record['authoruid'],
            'ispriv': record['ispriv'],
            'isanon': record['isanon'],
            #'pickeys': record['pickeys'],
            'ctime': record['ctime'],
        }

        dtime = datetime.fromtimestamp(int(record['ctime']))
        htime = (datetime.now() - dtime).seconds

        result['fctime'] = dtime.strftime('%Y-%m-%d %H:%M:%S')
        # TODO str to unicode
        result['hctime'] = str(htime/24/60/60)+'天前' if htime > 24*60*60 else str(htime/60/60)+'小时前' if htime > 60*60 else str(htime/60)+'分钟前' if htime > 60 else '刚刚'

        result['pickeys'] = map(lambda p:'http://7xi8l3.com1.z0.glb.clouddn.com/'+p, record['pickeys'])
        result['author'] = '一起去偷牛'
        result['avatar'] = 'http://7xi8l3.com1.z0.glb.clouddn.com/FravREnqYMS9MmIX5Y_YzaP6RUOJ'

        return result
