#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/7

Author: 

Description: 

"""

from conf import config
from model import base
from model import schema
from utiles import httpclient, random_tool
from handles.base import RESPONSE_STATUS_SUCCESS

BASE_URL = "https://{hostname}:{port}/api/".format(hostname=config.get("https_domain_name"),
                                                   port=config.get("https_listen_port"))
SESSION_ID = "XBItG2mcVkbClXFzYMkSELkRgYEnOMRo"


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
        raise Exception("init plover config failed!")


if __name__ == "__main__":
    base.clean_all_table()
    add_system_config()
