#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/2

Author: 

Description: 相关微信API调用

"""

import hashlib

from conf import config
from utiles import httpclient


def code2session(args):
    """
    
    :param args: 
    :return: 
    """
    return httpclient.get(url=config.get("code2session_url"), args=args)


def unifiedorder(args):
    """
    
    :param args: 
    :return: 
    """
    sign = wx_sign(args)
    args["sign"] = sign
    return httpclient.post(url=config.get("unifiedorder_url"), args=args, format="xml")


def wx_sign(args_dict):
    key_list = sorted([key for key in args_dict.keys()])
    args_list = ["%s=%s" % (key, args_dict[key]) for key in key_list if args_dict[key]]
    args_list.append("key=%s" % config.get("pay_key"))
    args_str1 = "&".join(args_list)

    m = hashlib.md5()
    m.update(args_str1.encode())
    args_str2 = m.hexdigest()

    return args_str2.upper()


if __name__ == "__main__":
    args_dict = dict(
        appid="wxd930ea5d5a258f4f",
        mch_id="10000100",
        device_info="1000",
        body="test",
        nonce_str="ibuaiVcKdpRxkhJA"
    )
    print(wx_sign(args_dict))
