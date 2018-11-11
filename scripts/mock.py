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
from model import base, schema

BASE_URL = "https://{hostname}:{port}/api/".format(hostname=config.get("https_domain_name"),
                                                   port=config.get("https_listen_port"))
USER_NUM = 50
SESSION_ID = "XBItG2mcVkbClXFzYMkSELkRgYEnOMRo"


def clear_db():
    base.clean_all_table()


def create_user():
    url = BASE_URL + "login"

    for i in range(USER_NUM):
        secret = random_tool.random_string(8)
        js_code = random_tool.random_string(16)
        post_vars = dict(appid=i + 1, secret=secret, js_code=js_code)
        args = dict(post_vars=post_vars)

        print("create user appid:{appid} secret:{secret} js_code:{js_code}".format(**post_vars))
        ret = httpclient.post(url, args)
        if ret["status"] != RESPONSE_STATUS_SUCESS:
            raise Exception("Mock user failed!")


def register_user():
    url = BASE_URL + "user"

    for i in range(USER_NUM):
        post_vars = dict(
            user_id=i + 1,
            user_info=json.dumps(dict(nickName=random_tool.random_chinese(3), gender=random_tool.random_int(1),
                                      avatarUrl=random_tool.random_string(12))),
            raw_data="",
            signature="",
            encrypted_data="",
            iv=""
        )
        args = dict(session_id=SESSION_ID, post_vars=post_vars)

        print("register user user_id:{user_id}".format(**post_vars))
        ret = httpclient.post(url, args)
        if ret["status"] != RESPONSE_STATUS_SUCESS:
            raise Exception("Register user failed: %s" % ret["message"])


def add_user_address():
    url = BASE_URL + "user/address"

    for i in range(USER_NUM):
        for j in range(random_tool.random_int(8)):
            post_vars = dict(
                user_id=i + 1,
                type=random_tool.random_int(1),
                property=random_tool.random_int(2),
                nick_name=random_tool.random_chinese(6),
                first_name=random_tool.random_chinese(1),
                last_name=random_tool.random_chinese(2),
                phone="1" + random_tool.random_digits(10),
                first_address=random_tool.random_chinese(random_tool.random_int(15, start=3)),
                last_address=random_tool.random_chinese(random_tool.random_int(15, start=3)),
                latitude=float("%s.%s" % (random_tool.random_int(90), random_tool.random_digits(10))),
                longitude=float("%s.%s" % (random_tool.random_int(180), random_tool.random_digits(10))),
                default=True if random_tool.random_int(1) else False
            )

            args = dict(session_id=SESSION_ID, post_vars=post_vars)
            print("add user:{user_id} address".format(**post_vars))
            ret = httpclient.post(url, args)
            if ret["status"] != RESPONSE_STATUS_SUCESS:
                raise Exception("Mock user address failed!")


def add_user_message():
    url = BASE_URL + "user/message"

    for i in range(USER_NUM):
        for j in range(random_tool.random_int(15)):
            post_vars = dict(
                user_id=i + 1,
                type=0,
                state=random_tool.random_int(1),
                title=random_tool.random_chinese(8),
                context=random_tool.random_chinese(25)
            )

            args = dict(session_id=SESSION_ID, post_vars=post_vars)
            print("add user:{user_id} message".format(**post_vars))
            ret = httpclient.post(url, args)
            if ret["status"] != RESPONSE_STATUS_SUCESS:
                raise Exception("Mock user message failed!")


if __name__ == "__main__":
    clear_db()
    create_user()
    register_user()
    add_user_address()
    add_user_message()
