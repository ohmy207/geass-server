 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [
    ('/([0-9]{9})/topic/new', app.NewTopicHandler),
    ('/[0-9]{9}/topic/([0-9a-f]{24})', app.DetailTopicHandler),
]
