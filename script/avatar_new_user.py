#-*- coding:utf-8 -*-

import realpath

import redis

from qiniu import Auth, BucketManager

from models.user import model as user_model
from config.global_setting import QINIU, REDIS_HOSTS, REDIS_KEYS


bucket_name = 'geass-avatar'
q = Auth(QINIU['access_key'], QINIU['secret_key'])
bucket = BucketManager(q)

conn = redis.Redis(host=REDIS_HOSTS[0][0], port=6379, db=1)
_user = user_model.User()


def get_avatar_by_uid(uid):
    user = _user.get_one({'_id': _user.to_objectid(uid)})
    return user['avatar'] if user and user['avatar'].startswith('http') else None


def update_avatar():
    uids =  conn.smembers(REDIS_KEYS['avatar_new_user_set'])
    print uids

    for uid in uids:
        avatar = get_avatar_by_uid(uid)
        if not avatar:
            continue
        ret, info = bucket.fetch(avatar, bucket_name)
        if not ret or 'error' in ret:
            print ret, info
            continue
        _user.update({'_id': _user.to_objectid(uid)}, {'$set': {'avatar': ret['key']}}, w=1)


if __name__ == '__main__':
    update_avatar()
