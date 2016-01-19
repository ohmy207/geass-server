# -*- coding:utf-8 -*-

import os
import sys

from setting import INSTALLED_APPS as _INSTALLED_APPS


# load app path into sys.path
def _app_path_load(dir_level_num=3):
    app_root_path = os.path.abspath(__file__)
    for i in xrange(0, dir_level_num):
        app_root_path = os.path.dirname(app_root_path)

    sys.path.append(app_root_path)


def pattern(prefix, handlers):
    urls = []
    for item in handlers:
        try:
            urlpattern = ('%s%s' % (prefix, item[0]), item[1], item[2])
        except:
            urlpattern = ('%s%s' % (prefix, item[0]), item[1])

        urls.append(urlpattern)

    return urls


# install app from settings
def _install_app():
    urlpatterns = []
    for item in _INSTALLED_APPS:
        module = __import__('.'.join(['apps', item]), None, None, [item], 0)
        try:
            urlpatterns += pattern(module.prefix, module.urls)
        except AttributeError:
            raise ImportError("No module named %s" % item)

    return urlpatterns

_app_path_load()

# router
urlpatterns = _install_app()
