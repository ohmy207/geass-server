 #-*- coding:utf-8 -*-

import app

prefix = ''

urls = [
    ('/t/new', app.NewTopicHandler),
    ('/t/([0-9a-f]{24})', app.DetailTopicHandler),
    ('/t/(follow|unfollow)', app.FollowTopicHandler),
    ('/u/personal', app.PersonalHandler),
    ('/u/(news|publish|follow)/list', app.PersonalListHandler),

    ('/p/new/submit', app.NewProposalHandler),
    ('/t/([0-9a-f]{24})/proposals', app.ListProposalHandler),
    ('/p/([0-9a-f]{24})', app.DetailProposalHandler),
    ('/p/(vote|unvote|revote)', app.VoteProposalHandler),

    ('/c/new/submit', app.NewCommentHandler),
    ('/t/([0-9a-f]{24})/comments', app.ListCommentHandler),
    ('/c/like', app.LikeCommentHandler),
]
