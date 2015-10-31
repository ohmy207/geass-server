#-*- coding:utf-8 -*-

import os


def is_test_file_exists():
    fname = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__))),
        '__test__')
    return os.path.isfile(fname)

if is_test_file_exists():
    TEST_MODE = True
    print '== Warning: Run in test mode!'
else:
    TEST_MODE = False


APP_HOST = 'http://geass.t207.me'
#REDIS_HOSTS = [('localhost', 6379, 0)]
REDIS = {
    'host': 'localhost',
    'port': 6379,

    'db': {
        'session': 0,
    },

    'key': {
    },
}

# cdn setting
CDN = {
    'is_disabled': False,
    'host': 'https://dn-geass-static.qbox.me/static'
}

# response message
# 0-100 reseved
MESSAGE = {
    0: u'成功',
    1: u'未知错误',
    2: u'url 找不到',
    3: u'参数错误',
    4: u'未登录',
    5: u'微信认证失败',
    6: u'用户已注册',

    30: u'内容不能为空',
    31: u'图片过多',

    51: u'话题已关注',
    52: u'话题未关注',
    71: u'已添加看法',
    72: u'已赞同看法',
    73: u'未赞同看法',
    81: u'评论已赞',
    91: u'已投票',
    92: u'未投票',
    93: u'之前投票不存在',

    100: u'昵称不能重复',
    101: u'昵称长度为2-16个',


    403: u'要先获取权限才能访问',
    404: u'资源不存在',
}

ERROR_PAGE_MESSAGE = {
    401: u'呜~获取用户信息没有成功。。',
    403: u'要先获取权限才能访问哦！',
    404: u'哦~好像没有找到要找的页面。。',
    500: u'啊~好像出错了。。',
}

ANONYMOUS_USER = {
    'nickname': '匿名用户',
    'avatar': 'https://dn-geass-static.qbox.me/anonymous_avatar.jpg',
}

# Third-party

# qiniu config
QINIU = {
    'access_key': '-T4p3--nu5Byod30detbf9SSrC-p9RmLrEJdG_gR',
    'secret_key': '7FB32WhNIgCNCHVyWko47WPHLlcXk6sN0EKgvgty',

    'bucket_name': {
        'image': 'geass-images',
        'avatar': 'geass-avatar',
    },

    'expires': 7200,

    'policy': {
        #'saveKey': '$(etag)$(ext)',
        'saveKey': '$(etag)',
        #'returnBody': 'key=$(key)hash=$(etag)ext$(ext)',
    },

    'img_url': 'https://dn-geass-images.qbox.me/',
    #'avatar_url': 'https://dn-geass-avatar.qbox.me/',
    'avatar_url': 'http://7xlbmo.com1.z0.glb.clouddn.com/',
    'thumb_suffix': '?imageView2/1/w/200/h/200',
}

# weixin config
WEIXIN = {

    # general
    'token': 'geass',
    'appid': 'wx02a1f4a182252307',
    'appsecret': 'a20441c7c4ffc64e193ed1c67f087441',

    # authorize
    'scope': {
        'scope_base': 'snsapi_base',
        'scope_userinfo': 'snsapi_userinfo',
    },

    'authorize_url_suffix': '#wechat_redirect',
    'authorize_url': 'https://open.weixin.qq.com/connect/oauth2/authorize',
    'access_token_url': 'https://api.weixin.qq.com/sns/oauth2/access_token',
    'userinfo_url': 'https://api.weixin.qq.com/sns/userinfo',

}

PIC_URL = {
    'avatar': lambda key: '%s%s' % (QINIU['avatar_url'], key),
    'img': lambda key: {'origin': '%s%s' % (QINIU['img_url'], key), 'thumb': '%s%s%s' % (QINIU['img_url'], key, QINIU['thumb_suffix'])},
}
