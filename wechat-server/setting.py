import logging
import os
import sys

from tornado.util import ObjectDict

from config.global_setting import REDIS, TEST_MODE
from utils import session

# app name
APP_NAME = 'geass-wechat'

# app base bapth
BASE_APP_DIR = os.path.dirname(os.path.abspath(__file__))
# project base path
BASE_PROJECT_DIR = os.path.dirname(BASE_APP_DIR)
sys.path.append(BASE_PROJECT_DIR)

# tornado web application settings
# details in http://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings
APPLICATION_SETTING = ObjectDict(
    static_path=os.path.join(BASE_APP_DIR, "static"),
    template_path=os.path.join(BASE_APP_DIR, "templates"),
    #xsrf_cookies=True,
    cookie_secret="jTlCsBtcTHCVkLIFJoSGidX5RToMfkr6uf34SU23S00=",
    #login_url="/wx/authorize/openid",
    login_url="/forbidden",
    #session_store=session.RedisSessionStore([(REDIS['host'], REDIS['port'], REDIS['db']['session'])])
    #autoescape=None,
)

# app setting
LOG_SETTING = ObjectDict(
    log_level=logging.INFO,
    log_path=os.path.join("/var/log/", APP_NAME+'.log'),
    log_size=500*1024*1024,
    log_count=3,
)

# check if app start in debug
if TEST_MODE:
#if os.path.exists(os.path.join(BASE_APP_DIR, '__test__')):
    APPLICATION_SETTING['debug'] = True
    LOG_SETTING.log_path = os.path.join("", APP_NAME+'.log')
    LOG_SETTING.log_level = logging.DEBUG
