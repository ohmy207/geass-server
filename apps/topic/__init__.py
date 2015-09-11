 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [
    ('/topics', app.TopicsHandler),
    ('/topics/([0-9a-f]{24})', app.DetailTopicHandler),

    ('/user', app.PersonalHandler),
    ('/user/publishing/(topics)', app.PublishingHandler),
    ('/user/following/(topics)', app.FollowingHandler),
    ('/user/news/(topics|votes|comments)', app.NewsHandler),

    ('/user/(vote|unvote|revote)/opinions', app.VoteOpinionHandler),
    ('/user/like/comments', app.LikeCommentHandler),

    ('/topics/([0-9a-f]{24})/opinions', app.OpinionsHandler),
    ('/opinions/([0-9a-f]{24})', app.DetailOpinionHandler),

    ('/topics/([0-9a-f]{24})/comments', app.CommentsHandler),
]
