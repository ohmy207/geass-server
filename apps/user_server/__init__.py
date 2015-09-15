 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),
    ('/(new|topic|opinion|comment_list|personal|news_list|following|publishing)', app.PageHandler),

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/base', app.BaseAuthorizeHandler),
    ('/wx/authorize/userinfo', app.UserinfoAuthorizeHandler),

]
