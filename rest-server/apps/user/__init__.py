 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/user', app.PersonalHandler),
    ('/user/publishing/(topics|opinions)', app.PublishingHandler),
    ('/user/following/topics', app.FollowingTopicHandler),
    ('/user/news/(topics|votes|comments)', app.NewsHandler),

    ('/user/voting/proposals/([0-9a-f]{24})', app.VoteProposalHandler),
    ('/user/approving/opinions/([0-9a-f]{24})', app.ApproveOpinionHandler),
    ('/user/liking/(topics|opinions)/comments/([0-9a-f]{24})', app.LikeCommentHandler),

    ('/(topics|opinions)/([0-9a-f]{24})/comments', app.CommentsHandler),

]
