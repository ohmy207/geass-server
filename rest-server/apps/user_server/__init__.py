 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/puppet_list', app.PuppetsHandler),

    ('/img/uptoken', app.UploadTokenHandler),
    ('/(|new|topic|proposal|opinion|comment_list|personal|notice_list|following|publish_topics|publish_opinions|help_list|help)', app.PageHandler),

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/base', app.BaseAuthorizeHandler),
    ('/wx/authorize/userinfo', app.UserInfoAuthorizeHandler),

]
