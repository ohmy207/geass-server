#-*- coding:utf-8 -*-

#from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler

from helpers import topic

logger = log.getLogger(__file__)


class NewTopicHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
            ('content', basestring),
        ],
        'option': [
            ('ispriv', bool, False),
            ('isanon', bool, False),
            ('pickeys', list, []),
        ]
    }

    #@authenticated
    def get(self, uid):
        self.render('new.html', uid=uid)

    #@authenticated
    def POST(self, uid):
        data = self._params
        data['authoruid'] = uid
        #data['content'] = data['content'].replace('\n', '<br/>')
        data['ctime'] = datetime.now()

        tid = topic['topic'].insert(data)

        self._jump = '/'+uid+'/t/'+unicode(tid)


class DetailTopicHandler(BaseHandler):

    _post_params = {
        'need': [
            ('title', basestring),
            ('content', basestring),
        ],
        'option': [
            ('ispriv', bool, False),
            ('isanon', bool, False),
            ('pickeys', list, []),
        ]
    }

    #@authenticated
    def get(self, tid):
        data = topic['topic'].get_one(topic['topic'].to_objectid(tid))
        self.render('detail.html', result=data)


class NewCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('content', basestring),
        ],
        'option': [
            ('tid', basestring, ''),
            ('pid', int, 0),
        ]
    }

    #@authenticated
    def POST(self):
        data = self._params
        data['authoruid'] = 111111111 #uid

        data['ctime'] = datetime.now()

        #coid = topic['comment'].insert(data)

        #self._jump = '/'+uid+'/t/'+unicode(tid)
        self._data = {
                'authorUid': data['authoruid'],
                'tid': data['tid'],
                'pid': data['pid'],
                'content': data['content'],
            }
