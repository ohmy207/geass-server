 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/topics/([0-9a-f]{24})/opinions', app.OpinionsHandler),
    ('/opinions/([0-9a-f]{24})', app.DetailOpinionHandler),

]
