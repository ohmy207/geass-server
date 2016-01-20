# -*- coding:utf-8 -*-

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


APP_HOST = 'http://geass.me'
# REDIS_HOSTS = [('localhost', 6379, 0)]
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
    'host': 'http://static.geass.me/static'
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
    401: u'获取用户信息没有成功。。',
    403: u'要先获取权限才能访问哦！',
    404: u'好像没有找到要找的页面。。',
    500: u'啊~好像出错了。。',
}

DEFAULT_USER = {
    'avatar': ('/static' if TEST_MODE else CDN['host']) + '/img/avatar.jpg',
}

ANONYMOUS_USER = {
    'nickname': '匿名用户',
    'avatar': DEFAULT_USER['avatar'],
}

# Third-party

# qiniu config
QINIU = {
    'access_key': '-T4p3--nu5Byod30detbf9SSrC-p9RmLrEJdG_gR',
    'secret_key': '7FB32WhNIgCNCHVyWko47WPHLlcXk6sN0EKgvgty',

    'bucket_name': {
        'avatar': 'geass-img1',
        'image': 'geass-img2',
    },

    'expires': 7200,

    'policy': {
        # 'saveKey': '$(etag)$(ext)',
        'saveKey': '$(etag)',
        # 'returnBody': 'key=$(key)hash=$(etag)ext$(ext)',
    },

    'avatar_url': 'http://img1.geass.me/',
    'img_url': 'http://img2.geass.me/',
    'thumb_suffix': '?imageView2/1/w/200/h/200',
}

# weixin config
WEIXIN = {

    # general
    'token': 'geass',
    'appid': 'wxa8e41846ff86c459',
    'appsecret': '8337c1065ac5eaf3e1a09f5dc71e3249',

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
