#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.user import model as user

logger = log.getLogger(__file__)

MODEL_SLOTS = ['User']


class User(user.User):

    @staticmethod
    def callback(record):
        result = {
            'tId':  record['_id'],
            'title': record['title'],
            'content': record['content'],
            'authorUid': record['auid'],
            'isPrivate': record['ispriv'],
            'isAnonymous': record['isanon'],
        }

        dtime = datetime.fromtimestamp(int(record['ctime']))
        htime = (datetime.now() - dtime).seconds

        result['fCreatedTime'] = dtime.strftime('%Y-%m-%d %H:%M:%S')
        # TODO str to unicode
        result['hCreatedTime'] = str(htime/24/60/60)+'天前' if htime > 24*60*60 else str(htime/60/60)+'小时前' if htime > 60*60 else str(htime/60)+'分钟前' if htime > 60 else '刚刚'

        result['picUrls'] = map(lambda p:'https://dn-geass-images.qbox.me/'+p, record['pickeys'])
        result['author'] = '一起去偷牛'
        result['avatar'] = 'http://7xi8l3.com1.z0.glb.clouddn.com/FravREnqYMS9MmIX5Y_YzaP6RUOJ'

        return result

