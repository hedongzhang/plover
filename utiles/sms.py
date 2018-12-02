#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/11

Author: 

Description: 短信接口

"""
import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

# 阿里认证key
ACCESS_KEY_ID = "LTAIT4Cx00yV2B28"
ACCESS_KEY_SECRET = "Zc0xK9ZyifsaQwNiJdskiFTEdja4xb"

# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)


def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    sms_request = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    sms_request.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        sms_request.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    sms_request.set_OutId(business_id)

    # 短信签名
    sms_request.set_SignName(sign_name)

    # 数据提交方式
    # sms_request.set_method(MT.POST)

    # 数据提交格式
    # sms_request.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    sms_request.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    sms_response = acs_client.do_action_with_exception(sms_request)
    response = json.loads(sms_response)

    if response["Code"] == "OK":
        return response

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
