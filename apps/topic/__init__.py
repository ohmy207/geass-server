 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [
    ('/([0-9]{9})/t/new', app.NewTopicHandler),
    ('/[0-9]{9}/t/([0-9a-f]{24})', app.DetailTopicHandler),

    ('/c/new/submit', app.NewProposalHandler),
    ('/t/([0-9a-f]{24})', app.ListProposalHandler),
    ('/[0-9]{9}/p/([0-9a-f]{24})', app.DetailProposalHandler),

    ('/[0-9]{9}/t/[0-9a-f]{24}/c/new', app.NewCommentHandler),
    ('/[0-9]{9}/t/([0-9a-f]{24})/c/page', app.PageCommentHandler),
    ('/[0-9]{9}/t/([0-9a-f]{24})/c/list', app.ListCommentHandler),
    ('/[0-9]{9}/c/like', app.LikeCommentHandler),
]
