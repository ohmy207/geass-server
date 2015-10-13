 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),
    ('/(new|topic|proposal|opinion|proposal_list|comment_list|personal|notice_list|following|publish_topics|publish_opinions)', app.PageHandler),

    ('/forbidden', app.ForbiddenHandler),
    ('/wx/authorize/base', app.BaseAuthorizeHandler),
    ('/wx/authorize/userinfo', app.UserInfoAuthorizeHandler),

]
