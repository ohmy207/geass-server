 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/topics', app.TopicsHandler),
    ('/topics/([0-9a-f]{24})', app.DetailTopicHandler),

    ('/topics/([0-9a-f]{24})/proposals', app.ProposalsHandler),
    ('/proposals/([0-9a-f]{24})', app.DetailProposalHandler),

    ('/topics/([0-9a-f]{24})/opinions', app.OpinionsHandler),
    ('/opinions/([0-9a-f]{24})', app.DetailOpinionHandler),

    ('/(topics|opinions)/([0-9a-f]{24})/comments', app.CommentsHandler),

]
