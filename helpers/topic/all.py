#-*- coding:utf-8 -*-

import log

from datetime import datetime

from models.topic import model as topic
from models.user import model as user

logger = log.getLogger(__file__)

MODEL_SLOTS = ['Topic', 'Proposal', 'Comment']


class Topic(topic.Topic):

    _user = user.User()

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

        user = Topic._user.get_one({'_id': Topic._user.to_objectid(record['auid'])})
        result['author'] = user['nickname']
        result['avatar'] = user['avatar']

        return result


class Proposal(topic.Proposal):

    _user = user.User()

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

        result['picUrls'] = map(lambda p:{'thumb': 'https://dn-geass-images.qbox.me/'+p+'?imageView2/1/w/200/h/200', 'origin': 'https://dn-geass-images.qbox.me/'+p}, record['pickeys'])

        user = Proposal._user.get_one({'_id': Proposal._user.to_objectid(record['auid'])})
        result['author'] = user['nickname']
        result['avatar'] = user['avatar']

        result['isLZ'] = True

        return result


class Comment(topic.Comment):

    _user = user.User()

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

        user = Comment._user.get_one({'_id': Comment._user.to_objectid(record['auid'])})
        touser = Comment._user.get_one({'_id': Comment._user.to_objectid(record['toauid'])})
        result['author'] = user['nickname']
        result['avatar'] = user['avatar']
        result['toAuthor'] = touser['nickname'] if touser else None
        result['isLZ'] = True

        return result
