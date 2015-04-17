#-*- coding:utf-8 -*-

# installed app list
INSTALLED_APPS = (
    'image',
    'topic',
)

# qiniu
QINIU_CONFIG = {
    'access_key': '-T4p3--nu5Byod30detbf9SSrC-p9RmLrEJdG_gR',
    'secret_key': '7FB32WhNIgCNCHVyWko47WPHLlcXk6sN0EKgvgty',

    'bucket_name': 'excalibur',
    'expires': 3600,

    'policy': {
        #'saveKey': '$(etag)$(ext)',
        'saveKey': '$(etag)',
        #'returnBody': 'key=$(key)hash=$(etag)ext$(ext)',
    },
}

# response message
#0-100 reseved
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
