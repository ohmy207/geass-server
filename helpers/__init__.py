#-*- coding:utf-8 -*-

from base import Helper as _Helper

from setting import INSTALLED_HELPERS as _INSTALLED_HELPERS, HELPER_PREFIX as _HELPER_PREFIX


def _install_helper():
    for item in _INSTALLED_HELPERS:
        # db model package
        package = __import__('.'.join(['helpers', item]), None, None, [item], 0)
        helper = _Helper()
        globals()[('%s%s')%(_HELPER_PREFIX, item)] = helper
        # all py files  included by package
        all_modules = getattr(package, '__all__', [])
        for module in all_modules:
            module =  __import__('.'.join(['helpers',item, module]),None, None, [module], 0)
            for model_name in getattr(module, 'MODEL_SLOTS', []):
                model = getattr(module, model_name, None)
                if model:
                    helper[model.__name__] = model()


_install_helper()
