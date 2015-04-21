#-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),

    #('/([0-9]{9})/t/new', app.PageHandler),
    ('/([0-9]{9})/t/([0-9a-f]{24}|new)', app.PageHandler),

]
