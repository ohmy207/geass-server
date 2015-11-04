#-*- coding:utf-8 -*-

import realpath

from helpers import wechat as wc


menu_data = {
    'button': [

        {
            'type': 'view',
            'name': '创建话题',
            'url': 'http://geass.me/new'
        },

        {
            'type': 'view',
            'name': '我的话题',
            'url': 'http://geass.me/personal'
        },

        {
            'name': '菜单',
            'sub_button': [

                {
                    'type': 'click',
                    'name': '意见建议',
                    'key': 'V1001_IDEA'
                },
                {
                    'type': 'click',
                    'name': '捐助',
                    'key': 'V1001_'
                },
                {
                    'type': 'click',
                    'name': '赞一下我们',
                    'key': 'V1001_GOOD'
                }

            ]
        }

    ]}

print wc['wechat'].create_menu(menu_data)
