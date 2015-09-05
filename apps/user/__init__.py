 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),
    ('/(new|topic|proposal|comments|personal|personal_list)', app.PageHandler),

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/base', app.BaseAuthorizeHandler),
    ('/wx/authorize/userinfo', app.UserinfoAuthorizeHandler),

]
