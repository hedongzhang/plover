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


def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):

    auth_str = "{code}{password}".format(code=code, password=password)
    m = hashlib.md5()
    m.update(auth_str.encode())
    args_str2 = m.hexdigest()

    httpclient.post()

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
    # 短信签名
    sign_name = "HDZhangTest"
    # 短信模板
    template_code = "SMS_151178627"
    # 模板参数
    template_param = '{"code":"%s"}' % code

    return send_sms(business_id, phone_numbers, sign_name, template_code, template_param=template_param)


def send_message(business_id, phone_numbers):
    # 短信签名
    sign_name = "HDZhangTest"
    # 短信模板
    template_code = "SMS_151178627"
    # 模板参数
    template_param = '{"code":"%s"}' % "tack"

    return send_sms(business_id, phone_numbers, sign_name, template_code, template_param=template_param)


if __name__ == '__main__':
    session_id = "dscdscdscdscsdwefregret"
    print(send_verification_code(session_id, "17316923416", "qnmlgb"))
