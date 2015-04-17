# -*- coding:utf-8 -*-
import logging
import os

# app path
CUR_PATH = os.path.dirname(os.path.abspath(__file__))

# app start status
DEBUG = False

# template path
TEMPLATE_PATH = os.path.join(CUR_PATH, "templates")

# static path
STATIC_PATH = os.path.join(CUR_PATH, "static")

# app name
APP_NAME = 'geass-server'

# server name this name is equal sever dir name
SERVER_NAME = 'geass-server'

if os.path.exists(os.path.join(CUR_PATH, '__test__')):
    DEBUG = True

# cross site attack
XSRF_COOKIES = False

# cookie secret
COOKIE_SECRET = 'aVD321fQAGaYdkLlsd334K#/adf22iNvdfdflle3fl$='

# REDIS_HOST = [('jxqctk', 6379, 0), ('jxqctl', 6379, 0)]
REDIS_HOST = [('localhost', 6379, 0)]
# log path
LOG_PATH = '/var/log/'

# log max size per file (bytes inc)
LOG_MAX_SIZE = 500 * 1024 * 1024

# log file count
LOG_MAX_COUNT = 3

if DEBUG:
    LOG_FILENAME = '%s.log' % APP_NAME
    REDIS_HOST = [('localhost', 6379, 0)]
else:
    LOG_FILENAME = '%s%s.log' % (LOG_PATH, APP_NAME)
    REDIS_HOST = [('jxqctk', 6379, 0), ('jxqctl', 6379, 0)]


def _init_logging():
    formatter = logging.Formatter(
        '%(levelname)s:%(asctime)s %(name)s:%(lineno)d:%(funcName)s %(message)s')
    simple_formater = logging.Formatter(
        '%(levelname)s:%(name)s:%(lineno)d:%(funcName)s %(message)s')

    # formatter = logging.Formatter('%(levelname)-6s %(asctime)s %(name)-8s %(module)s %(lineno)d %(funcName)s %(message)s')
    # root log level is debug mode
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # dev log level is debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(simple_formater)

    # file log level is warning mode
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=LOG_MAX_SIZE, backupCount=LOG_MAX_COUNT)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)


_init_logging()
