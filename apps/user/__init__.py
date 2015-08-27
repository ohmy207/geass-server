 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/(openid|userinfo)', app.WeiXinAuthorizeHandler),

]
