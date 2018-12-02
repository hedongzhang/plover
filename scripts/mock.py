#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/7

Author: 

Description: 

"""

import json

from conf import config
from handles.base import RESPONSE_STATUS_SUCCESS, CALLBACK_RESPONSE_SUCCESS_CODE
from handles.wx_api import wx_sign
from model import base, schema
from utiles import httpclient, random_tool

BASE_URL = "https://{hostname}:{port}/api/".format(hostname=config.get("https_domain_name"),
                                                   port=config.get("https_listen_port"))
USER_NUM = 30
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
        if ret["status"] != RESPONSE_STATUS_SUCCESS:
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
        if ret["status"] != RESPONSE_STATUS_SUCCESS:
            raise Exception("Register user failed: %s" % ret["message"])


def add_user_address():
    url = BASE_URL + "user/address"

    for i in range(USER_NUM):
        for j in range(random_tool.random_int(8)):
            post_vars = dict(
                user_id=i + 1,
                type=random_tool.random_int(1),
                property=random_tool.random_int(2),
                shop_name=random_tool.random_chinese(6),
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
            if ret["status"] != RESPONSE_STATUS_SUCCESS:
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
            if ret["status"] != RESPONSE_STATUS_SUCCESS:
                raise Exception("Mock user message failed!")


def add_system_config():
    url = BASE_URL + "config"

    post_vars = dict(
        amount_per_order="2.2",
        draw_cratio="0.2",
        deposit="20",
        # 文案
        master_title="这次，不需要自己拿",
        master_desc="即使再忙，也别太累",
        master_banner="同学帮送，快速送达",
        slave_title="这次，赚点零花钱",
        slave_desc="空闲之余，也有所得"
    )
    args = dict(session_id=SESSION_ID, post_vars=post_vars)
    print("init plover config:{post_vars}".format(post_vars=post_vars))
    ret = httpclient.post(url, args)
    if ret["status"] != RESPONSE_STATUS_SUCCESS:
        raise Exception("Mock plover config failed!")


def deposit():
    """
    缴纳押金
    :return: 
    """
    url = BASE_URL + "user/account/actions/deposit"

    for i in range(USER_NUM):
        if random_tool.random_int(1):
            post_vars = dict(
                user_id=i + 1,
                amount=random_tool.random_int(10000, start=100) / 100
            )
            args = dict(session_id=SESSION_ID, post_vars=post_vars)
            print("deposit:{post_vars}".format(post_vars=post_vars))
            ret = httpclient.post(url, args)
            if ret["status"] != RESPONSE_STATUS_SUCCESS:
                raise Exception("deposit user_id:%s failed!" % i + 1)

            url1 = url + "/%s" % ret["data"]["id"]
            args1 = dict(
                return_code="SUCCESS",
                return_msg="OK",
                total_fee=post_vars["amount"],
                transaction_id=random_tool.random_string()
            )
            args1["sign"] = wx_sign(args1)

            ret1 = httpclient.post(url1, args1, format="xml")
            if ret1["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                raise Exception("deposit user_id:%s callback failed! err:%s" % (i + 1, ret1["return_msg"]))


if __name__ == "__main__":
    clear_db()
    create_user()
    register_user()
    add_user_address()
    add_user_message()
    add_system_config()
    deposit()
