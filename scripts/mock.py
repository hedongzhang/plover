#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/7

Author: 

Description: 

"""

import json

from handles.base import RESPONSE_STATUS_SUCESS
from utiles import httpclient, config, random_tool


def create_user():
    url = "https://{hostname}:{port}/api/login".format(hostname=config.get("https_domain_name"),
                                                       port=config.get("https_listen_port"))

    for i in range(30):
        secret = random_tool.random_string(8)
        js_code = random_tool.random_string(16)
        post_vars = dict(appid=i+1, secret=secret, js_code=js_code)
        args = dict(post_vars=post_vars)

        print("create user appid:{appid} secret:{secret} js_code:{js_code}".format(**post_vars))
        ret = httpclient.post(url, args)
        if ret["status"] != RESPONSE_STATUS_SUCESS:
            raise Exception("Mock user failed!")


def register_user():
    url = "https://{hostname}:{port}/api/user".format(hostname=config.get("https_domain_name"),
                                                      port=config.get("https_listen_port"))

    for i in range(30):
        session_id = random_tool.random_string(16)
        post_vars = dict(
            user_id=i+1,
            user_info=json.dumps(dict(nickName=random_tool.random_chinese(3), gender=random_tool.random_int(1),
                                      avatarUrl=random_tool.random_string(12))),
            raw_data="",
            signature="",
            encrypted_data="",
            iv=""
        )
        args = dict(session_id=session_id, post_vars=post_vars)

        print("register user user_id:{user_id}".format(**post_vars))
        ret = httpclient.post(url, args)
        if ret["status"] != RESPONSE_STATUS_SUCESS:
            raise Exception("Register user failed: %s" % ret["message"])


if __name__ == "__main__":
    create_user()
    register_user()
