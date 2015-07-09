 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [
    ('/([0-9]{9})/t/new', app.NewTopicHandler),
    ('/[0-9]{9}/t/([0-9a-f]{24})', app.DetailTopicHandler),

    ('/c/new/submit', app.NewCommentHandler),
]
