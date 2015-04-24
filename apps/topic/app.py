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
