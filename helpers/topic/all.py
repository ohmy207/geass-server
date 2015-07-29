#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.topic import model as topic

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Comment']


class Topic(topic.Topic):

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


class Proposal(topic.Proposal):

    @staticmethod
    def callback(record):
        result = {
            'tId': record['tid'],
            'pId': record['_id'],
            'content': record['content'],
            'authorUid': record['auid'],
            'voteNum': record['vnum'],
        }

        dtime = datetime.fromtimestamp(int(record['ctime']))
        htime = (datetime.now() - dtime).seconds

        result['fCreatedTime'] = dtime.strftime('%Y-%m-%d %H:%M:%S')
        # TODO str to unicode
        result['hCreatedTime'] = str(htime/24/60/60)+'天前' if htime > 24*60*60 else str(htime/60/60)+'小时前' if htime > 60*60 else str(htime/60)+'分钟前' if htime > 60 else '刚刚'

        result['picUrls'] = map(lambda p:'https://dn-geass-images.qbox.me/'+p, record['pickeys'])
        result['author'] = '一起去偷牛'
        result['avatar'] = 'http://7xi8l3.com1.z0.glb.clouddn.com/FravREnqYMS9MmIX5Y_YzaP6RUOJ'
        result['isLZ'] = True

        return result


class Comment(topic.Comment):

    @staticmethod
    def callback(record):
        result = {
            'tId': record['tid'],
            'pId': record['_id'],
            #'toPId': record['topid'],
            'content': record['content'],
            'authorUid': record['auid'],
            'likeNum': record['lnum'],
        }

        dtime = datetime.fromtimestamp(int(record['ctime']))
        htime = (datetime.now() - dtime).seconds

        result['fCreatedTime'] = dtime.strftime('%Y-%m-%d %H:%M:%S')
        # TODO str to unicode
        result['hCreatedTime'] = str(htime/24/60/60)+'天前' if htime > 24*60*60 else str(htime/60/60)+'小时前' if htime > 60*60 else str(htime/60)+'分钟前' if htime > 60 else '刚刚'

        result['author'] = '一起去偷牛'
        result['toAuthor'] = '一起去偷牛' if record['topid'] else None
        result['avatar'] = 'http://7xi8l3.com1.z0.glb.clouddn.com/FravREnqYMS9MmIX5Y_YzaP6RUOJ'
        result['isLZ'] = True

        return result
