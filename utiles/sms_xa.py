#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/3

Author: 

Description: 

"""

import json
import hashlib

from utiles import httpclient

uid = "81347"
code = "ynwl"
password = "OPrh5F4"

url = "http://sms.10690221.com:9011/hy/"


def send_sms(phone_numbers, message):
    auth_str = "{code}{password}".format(code=code, password=password)
    m = hashlib.md5()
    m.update(auth_str.encode())
    auth = m.hexdigest()

    args = dict(
        uid=uid,
        auth=auth,
        mobile=phone_numbers,
        msg=message,
        expid=0,
        encode="utf-8"
    )
    httpclient.get(url, args)

    retry_count = 2
    while retry_count:
        sms_response = acs_client.do_action_with_exception(sms_request)
        response = json.loads(sms_response)

        if response["Code"] == "OK":
            return response
        else:
            retry_count -= 1

    raise Exception("短信接口调用异常, 错误码:{code}".format(code=response["Code"]))


def send_verification_code(business_id, phone_numbers, code):
    message = "您的验证码：%s，您正进行身份验证，打死不告诉别人！" % code
    send_sms(phone_numbers, message)


def send_message(business_id, phone_numbers, message):
    send_sms(phone_numbers, message)


if __name__ == '__main__':
    session_id = "dscdscdscdscsdwefregret"
    print(send_verification_code(session_id, "17316923416", "qnmlgb"))
