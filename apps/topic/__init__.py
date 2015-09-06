 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [
    ('/topics', app.TopicsHandler),
    ('/topics/([0-9a-f]{24})', app.DetailTopicHandler),

    ('/user', app.PersonalHandler),
    ('/user/(topics)', app.PublishingHandler),
    ('/user/following/(topics)', app.FollowingHandler),
    ('/user/news/(topics)', app.NewsHandler),

    ('/user/(vote|unvote|revote)/proposals', app.VoteProposalHandler),
    ('/user/like/comments', app.LikeCommentHandler),

    ('/topics/([0-9a-f]{24})/proposals', app.ProposalsHandler),
    ('/proposals/([0-9a-f]{24})', app.DetailProposalHandler),

    ('/topics/([0-9a-f]{24})/comments', app.CommentsHandler),
]
