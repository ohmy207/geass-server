# -*- coding:utf-8 -*-

# from pymongo import DESCENDING

import db as _db
from setting import MONGO_DB_MAPPING as _MONGO_DB_MAPPING
from utils.util import import_object


class MixinModel(_db.MixinModel):

    _instance = {}

    @staticmethod
    def instance(name):
        if not MixinModel._instance.get(name):
            model_name = name.split('.')
            ins_name = '.'.join(['models', model_name[0], 'model', model_name[1]])
            MixinModel._instance[name] = import_object(ins_name)()

        return MixinModel._instance[name]


class BaseModel(_db.BaseModel, MixinModel):

    def __init__(self, db_name='test'):
        super(BaseModel, self).__init__(db_name, _MONGO_DB_MAPPING)

    def get_all(self, spec=None, skip=0, limit=20, order=None, sort=None):

        # if order:
        #     sort = order == 'new' and [('ctime', DESCENDING)] or (order == 'hot' and [('rank', DESCENDING)]) or sort

        return self.to_str(self.find(spec=spec, skip=skip, limit=limit, sort=sort), self.callback if hasattr(self, 'callback') else None)

    def get_one(self, objid):

        if isinstance(objid, str):
            objid = self.to_objectid(objid)
        rd = self.find_one(objid) or None
        if rd:
            if hasattr(self, 'callback'):
                return self.callback(self.to_one_str(rd))

            return self.to_one_str(rd)
        return None

    def get_related_album(self, module):
        pass

    def get_count(self, spec=None):
        return self.find(spec=spec).count()
