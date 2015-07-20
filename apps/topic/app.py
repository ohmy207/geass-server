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

    #@authenticated
    def get(self, tid):
        data = topic['topic'].get_one(topic['topic'].to_objectid(tid))
        self.render('detail.html', result=data)


class NewProposalHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('content', basestring),
        ],
        'option': [
            ('pickeys', list, []),
        ]
    }

    #@authenticated
    def POST(self):
        data = self._params

        data['tid'] = topic['proposal'].to_objectid(data['tid'])
        data['authoruid'] = 111111111
        data['ctime'] = datetime.now()

        pid = topic['proposal'].insert(data)
        data = topic['proposal'].get_one(pid)

        self._data = data


class ListProposalHandler(BaseHandler):

    _get_params = {
        'need': [
        ],
        'option': [
            ('skip', int, 0),
            ('limit', int, 5),
        ]
    }

    #@authenticated
    def GET(self, tid):
        spec = {'tid': topic['proposal'].to_objectid(tid)}
        data_list = topic['proposal'].get_all(spec, skip=self._skip, limit=self._limit)
        self._data = {
                'dataList': data_list,
                'nextStart': self._skip + self._limit
            }
