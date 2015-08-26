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

    40: u'邮箱或密码不能为空',
    41: u'邮箱或密码错误',
    49: u'登录失败',
    50: u'社交登录失败',
    51: u'账号已被绑定',
    52: u'Email 已经被注册',
    53: u'Email 不存在',
    60: u'评论不能为空',
    100: u'昵称不能重复',
    101: u'昵称长度为2-16个',


    404: u'not found',
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

    'expires': 3600,

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
