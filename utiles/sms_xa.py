#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/3

Author: 

Description: 

"""

import hashlib
from tornado import httpclient

uid = "81347"
code = "ynwl"
password = "OPrh5F4"

url = "http://sms.10690221.com:9011/hy/"


def send_sms(phone_numbers, message):
    global url
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

    http_client = httpclient.HTTPClient()
    try:

        args_str = "&".join(["{key}={value}".format(key=k, value=v) for k, v in args.items()])
        url += "?" + args_str
        http_request = httpclient.HTTPRequest(url=url, method="GET", request_timeout=60)
        response = http_client.fetch(http_request)

        ret = response.body.decode('utf-8').split(",")
        if int(ret[0]) != 0:
            raise Exception("错误码:%s, 错误信息:%s" % (ret[0], ret[1] if len(ret) > 1 else ""))

    except Exception as e:
        raise Exception("调用短信接口失败:%s" % e)
    finally:
        http_client.close()


def send_verification_code(business_id, phone_numbers, code):
    message = "您的验证码：%s，您正进行身份验证，打死不告诉别人！" % code
    send_sms(phone_numbers, message)


def send_message(business_id, phone_numbers, message):
    send_sms(phone_numbers, message)


if __name__ == '__main__':
    session_id = "dscdscdscdscsdwefregret"
    print(send_verification_code(session_id, "17316923416", "qnmlgb"))
