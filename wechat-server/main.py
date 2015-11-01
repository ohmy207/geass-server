#-*- coding:utf-8 -*-

import sys
import os

import tornado.web
import tornado.httpserver
import tornado.options

from tornado.options import define, options

from apps import urlpatterns
from setting import APPLICATION_SETTING, LOG_SETTING

import log

define("port", default=8888, type=int)

logger = log.getLogger(**LOG_SETTING)


class ErrorHandler(tornado.web.RequestHandler):

    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        self.render('404.html', error_code=self._status_code)
        #self.write(unicode(self._status_code))
        #self.redirect('/error')


class Application(tornado.web.Application):

    def __init__(self):

        handlers = urlpatterns
        settings = APPLICATION_SETTING

        tornado.web.Application.__init__(self, handlers, **settings)
        tornado.web.ErrorHandler = ErrorHandler


def main():
    print 'geass-wechat started!'
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.start()


if __name__ == '__main__':
    main()
