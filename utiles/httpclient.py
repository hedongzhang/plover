#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import json

from tornado import httpclient
from conf import config
from utiles import xml


def get(url, args, format="json", timeout=60):
    """
    发起GET请求, 注意: 仅支持json格式协议
    :param url: 
    :param args: 字典格式的参数类型
    :param format: 协议格式
    :param timeout: 
    :return: 
    """
    http_client = httpclient.HTTPClient()
    try:
        args_str = "&".join(["{key}={value}".format(key=k, value=v) for k, v in args.items()])
        url += "?" + args_str
        http_request = httpclient.HTTPRequest(url=url, method="GET", request_timeout=timeout)
        response = http_client.fetch(http_request)

        if format == "json":
            ret = json.loads(response.body)
        elif format == "xml":
            ret = xml.loads(response.body)
        else:
            raise Exception("format is invalid")

        return ret
    finally:
        http_client.close()


def post(url, args, format="json", timeout=60):
    """
    发起POST请求
    :param url: 
    :param args: 字典格式的参数类型
    :param format: 协议格式
    :param timeout: 
    :return: 
    """
    http_client = httpclient.HTTPClient()

    if format == "json":
        body = json.dumps(args)
    elif format == "xml":
        body = xml.dumps(args)
    else:
        raise Exception("format is invalid")

    http_request = httpclient.HTTPRequest(url=url, method="POST", body=body, request_timeout=timeout)
    response = http_client.fetch(http_request)

    if format == "json":
        ret = json.loads(response.body)
    elif format == "xml":
        ret = xml.loads(response.body)
    else:
        raise Exception("format is invalid")

    return ret


def post_by_cert(url, args, format="json", timeout=60):
    """
    发起POST请求
    :param url: 
    :param args: 字典格式的参数类型
    :param format: 协议格式
    :param timeout: 
    :return: 
    """
    ssl_options = dict(certfile=config.get("wx_certfile"), keyfile=config.get("wx_keyfile"))
    http_client = httpclient.HTTPClient()

    if format == "json":
        body = json.dumps(args)
    elif format == "xml":
        body = xml.dumps(args)
    else:
        raise Exception("format is invalid")

    http_request = httpclient.HTTPRequest(url=url, method="POST", body=body, request_timeout=timeout,
                                          ssl_options=ssl_options)
    response = http_client.fetch(http_request)

    if format == "json":
        ret = json.loads(response.body)
    elif format == "xml":
        ret = xml.loads(response.body)
    else:
        raise Exception("format is invalid")

    return ret


if __name__ == '__main__':
    print(get("https://hdzhang.xyz:443/api/user", dict(session_id="4d85a07e-3ed8-4515-adc4-d03b41b28aff", user_id=1)))
