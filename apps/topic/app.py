#-*- coding:utf-8 -*-

#from tornado.web import authenticated

import log

from datetime import datetime

from apps.base import BaseHandler
from apps.base import ResponseError

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
        self.render('topic_new.html', uid=uid)

    #@authenticated
    def POST(self, uid):
        data = self._params
        data['auid'] = uid
        #data['content'] = data['content'].replace('\n', '<br/>')
        data['ctime'] = datetime.now()

        tid = topic['topic'].insert(data)

        self._jump = '/'+uid+'/t/'+unicode(tid)


class DetailTopicHandler(BaseHandler):

    #@authenticated
    def get(self, tid):
        data = topic['topic'].get_one(topic['topic'].to_objectid(tid))
        self.render('topic_detail.html', result=data)


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
        data['auid'] = 111111111
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


class DetailProposalHandler(BaseHandler):

    #@authenticated
    def get(self, pid):
        data = topic['proposal'].get_one(topic['proposal'].to_objectid(pid))
        self.render('proposal_detail.html', result=data)



class NewCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('content', basestring),
        ],
        'option': [
            ('topid', basestring, None),
        ]
    }

    #@authenticated
    def POST(self):
        data = self._params

        data['tid'] = topic['comment'].to_objectid(data['tid'])
        data['topid'] = topic['comment'].to_objectid(data['topid'])
        data['toauid'] = topic['comment'].find_one({'_id': data['topid']}).get('auid', None) if data['topid'] else None
        data['auid'] = 111111111
        data['ctime'] = datetime.now()

        coid = topic['comment'].insert(data)
        data = topic['comment'].get_one(coid)

        self._data = data


class PageCommentHandler(BaseHandler):

    #@authenticated
    def get(self, tid):
        data = {'tId': tid}
        self.render('comment_list.html', result=data)


class ListCommentHandler(BaseHandler):

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
        spec = {'tid': topic['comment'].to_objectid(tid)}
        data_list = topic['comment'].get_all(spec, skip=self._skip, limit=self._limit)

        self._data = {
            'dataList': data_list,
            'nextStart': self._skip + self._limit
        }


class LikeCommentHandler(BaseHandler):

    _post_params = {
        'need': [
            ('tid', basestring),
            ('coid', basestring),
        ],
        'option': [
        ]
    }

    #@authenticated
    def POST(self):
        data = self._params
        uid = 111111111

        coid = topic['comment'].to_objectid(data['coid'])
        comment = topic['comment'].find_one({'_id': coid})

        if not comment:
            raise ResponseError(404)

        if uid in comment['like']:
            raise ResponseError(404)

        topic['comment'].update({'_id': coid}, {'$inc': {'lnum': 1}, '$push': {'like': uid}}, w=1)

        self._data = {
            'likeNum': 1,
        }
