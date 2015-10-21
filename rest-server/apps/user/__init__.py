 #-*- coding:utf-8 -*-

import app

prefix = '/api/v1'

urls = [

    ('/user', app.PersonalHandler),
    ('/user/(topics|opinions|following)', app.UserSourceHandler),
    ('/user/notifications', app.NotificationHandler),

    ('/user/following/topics/([0-9a-f]{24})', app.FollowTopicHandler),
    ('/user/voting/proposals/([0-9a-f]{24})', app.VoteProposalHandler),
    ('/user/approving/opinions/([0-9a-f]{24})', app.ApproveOpinionHandler),
    ('/user/liking/(topics|opinions)/comments/([0-9a-f]{24})', app.LikeCommentHandler),

]
