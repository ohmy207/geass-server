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

## Third-party

# qiniu config
QINIU = {
    'access_key': '-T4p3--nu5Byod30detbf9SSrC-p9RmLrEJdG_gR',
    'secret_key': '7FB32WhNIgCNCHVyWko47WPHLlcXk6sN0EKgvgty',

    'bucket_name': 'geass-images',
    'expires': 3600,

    'policy': {
        #'saveKey': '$(etag)$(ext)',
        'saveKey': '$(etag)',
        #'returnBody': 'key=$(key)hash=$(etag)ext$(ext)',
    },
}

# weixin config
WX = {

    # general
    'token': 'geass',
    'appid': 'wx02a1f4a182252307',
    'appsecret': 'a20441c7c4ffc64e193ed1c67f087441',

    # authorize
    'scope_base': 'snsapi_base',
    'scope_userinfo': 'snsapi_userinfo',

}

# TODO line so long
WX_URL = {

    'authorize_url': lambda redirect_uri, scope, state: 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=%s&state=%s#wechat_redirect' % (WX['appid'], redirect_uri, scope, state),

    'access_token_url': lambda code: 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (WX['appid'], WX['appsecret'], code),

}
