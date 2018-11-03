#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import json

from tornado import httpclient


def get(url, args, timeout=60):
    """
    发起GET请求, 注意: 仅支持json格式协议
    :param url: 
    :param args: 字典格式的参数类型
    :param timeout: 
    :return: 
    """
    http_client = httpclient.HTTPClient()
    try:
        args_str = "&".join(["{key}={value}".format(key=k, value=v) for k, v in args.items()])
        url += "?" + args_str
        http_request = httpclient.HTTPRequest(url=url, method="GET", request_timeout=timeout)
        response = http_client.fetch(http_request)
        return json.loads(response.body)
    finally:
        http_client.close()


def post(url, args, timeout=60):
    """
    发起POST请求, 注意: 仅支持json格式协议
    :param url: 
    :param args: 字典格式的参数类型
    :param timeout: 
    :return: 
    """
    http_client = httpclient.HTTPClient()
    http_request = httpclient.HTTPRequest(url=url, method="POST", body=json.dumps(args), request_timeout=timeout)
    response = http_client.fetch(http_request)
    return json.loads(response.body)


if __name__ == '__main__':
    print(get("https://hdzhang.xyz:443/api/user", dict(session_id="4d85a07e-3ed8-4515-adc4-d03b41b28aff", user_id=1)))
