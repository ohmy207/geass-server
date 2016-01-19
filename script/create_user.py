# -*- coding:utf-8 -*-

import time

import realpath
from helpers import user as _user

nicknames = ['x杯子', 'Neo', '阿甘会飞', '沉睡の狗', '路亽曱', '浑浑噩噩',
             '含笑饮毒酒', '落婲丶無痕', '失心疯', '呆呆熊', 'kimpvp',
             '一杯奶昔', '小柠丶', '折君zZ', '提督1号', '松娘欸', '小兵233',
             '很好饿', 'JaeSN', '拿破仑吃饭']

for i in range(len(nicknames)):
    user = {
        'nickname': '',
        'sex': '1',
        'avatar': ''
    }

    user['nickname'] = nicknames[i]
    user['avatar'] = 'puppet%s.jpg' % (i+1)

    print i+1
    print user['nickname'], user['avatar']

    print _user['user'].create(user)
    print user
    print ''

    time.sleep(1)
