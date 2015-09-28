 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/user', app.PersonalHandler),
    ('/user/publishing/(topics|opinions)', app.PublishingHandler),
    ('/user/following/topics', app.FollowingTopicHandler),
    ('/user/news/(topics|votes|comments)', app.NewsHandler),

    ('/user/(vote|unvote|revote)/proposals', app.VoteProposalHandler),
    ('/user/approve/opinions', app.ApproveOpinionHandler),
    ('/user/like/comments', app.LikeCommentHandler),

    ('/topics/([0-9a-f]{24})/comments', app.CommentsHandler),

]
