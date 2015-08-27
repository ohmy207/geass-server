 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),
    ('/(new|topic|proposal|comments)', app.PageHandler),

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/(openid|userinfo)', app.WeiXinAuthorizeHandler),

]
