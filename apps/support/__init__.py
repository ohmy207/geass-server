#-*- coding:utf-8 -*-

import app

prefix = ''

urls = [

    ('/img/uptoken', app.UploadTokenHandler),

    ('/wx/check', app.CheckSignatureHandler),

]
