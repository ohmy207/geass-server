 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/topics', app.TopicsHandler),
    ('/topics/([0-9a-f]{24})', app.DetailTopicHandler),

]
